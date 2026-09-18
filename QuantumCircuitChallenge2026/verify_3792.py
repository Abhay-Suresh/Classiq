#!/usr/bin/env python3
"""
Full statevector verification for the D2 Interleaved Edges circuit (Depth 3,792).
"""
import re
import warnings
from pathlib import Path
import numpy as np
import classiq
from classiq import *
from classiq.qmod.symbolic import pi
from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings

warnings.filterwarnings("ignore")

GRID_SIZE = 64
COORD_BITS = 6

def logo_pixel(x: int, y: int) -> bool:
    return (
        (2 <= x <= 26 and 29 <= y <= 53)
        or (26 <= x <= 49 and 39 <= y <= 43)
        or (x - 55) ** 2 + (y - 41) ** 2 <= 42
        or (x - 40) ** 2 + (y - 19) ** 2 <= 72
    )

@qperm
def oracle_d2_edges_middle(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    # 1. Largest regions
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # 2. D1 outer shells
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # 3. D2 interleaved edges
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))

@qfunc
def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
    allocate(x)
    allocate(y)
    hadamard_transform(x)
    hadamard_transform(y)
    oracle_d2_edges_middle(x, y)

print("Synthesizing D2 Interleaved Edges model...")
model = create_model(main, constraints=Constraints(
    optimization_parameter=OptimizationParameter.DEPTH, max_width=18))
qprog = synthesize(model)

raw_qasm = export(qprog, TargetLanguage.QASM2)
raw_lines = raw_qasm.splitlines()
prep_idx = {i for i, l in enumerate(raw_lines)
            if l.strip().startswith('hadamard_transform_') and 'q[' in l}
candidate_qasm = '\n'.join(l for i, l in enumerate(raw_lines) if i not in prep_idx)
candidate_qprog = quantum_program_from_qasm(candidate_qasm)

print("Transpiling with INTENSIVE option...")
transpiled = classiq.transpile(
    candidate_qprog,
    preferences=Preferences(
        transpilation_option=TranspilationOption.INTENSIVE,
        custom_hardware_settings=CustomHardwareSettings(basis_gates=['u3', 'cx']),
    ),
)
metrics = classiq.get_transpiled_circuit_metrics(transpiled)
print(f"Width:    {metrics.width}")
print(f"Depth:    {metrics.depth}")
print(f"CX count: {metrics.count_ops.get('cx', 0)}")

submission_qasm = export(
    transpiled,
    TargetLanguage.QASM2,
    transpilation_config=TranspilationConfig(
        transpilation_level=TranspilationOption.INTENSIVE,
        basis_gates=['u3', 'cx'],
    ),
)

# Run full statevector verification
print("\nVerifying correctness with 3 random product states...")
STATE_ERROR_THRESHOLD = 1e-10
NORMALIZATION_ERROR_THRESHOLD = 1e-10

def dense_classiq_statevector(frame, width: int):
    statevector = np.zeros(1 << width, dtype=np.complex128)
    for row in frame.itertuples(index=False):
        bitstring = str(row.bitstring).replace(" ", "")
        statevector[int(bitstring, 2)] = complex(row.amplitude)
    normalization_error = abs(np.vdot(statevector, statevector).real - 1)
    return statevector, normalization_error

submission_source = submission_qasm
logical_size = GRID_SIZE**2
rng = np.random.default_rng(42)
random_phases = rng.uniform(-np.pi, np.pi, size=(3, 2 * COORD_BITS))
target_phases = np.array(
    [-1 if logo_pixel(x, y) else 1 for y in range(GRID_SIZE) for x in range(GRID_SIZE)],
    dtype=np.complex128,
)

source_without_comments = re.sub(r"//[^\n]*", lambda m: " " * len(m.group()), submission_source)
qreg_matches = list(re.finditer(rf"\bqreg\s+q\s*\[\s*18\s*\]\s*;", source_without_comments))
insertion_index = qreg_matches[0].end()
basis = np.arange(logical_size, dtype=np.uint16)
max_error = ancilla_error = normalization_error = 0.0
shared_global_phase = 1 + 0j

with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    for test_index, phases in enumerate(random_phases):
        preparation = [f"u3(pi/2,{phase:.17g},0) q[{qubit}];" for qubit, phase in enumerate(phases)]
        test_qasm = submission_source[:insertion_index] + "\n" + "\n".join(preparation) + submission_source[insertion_index:]
        with ExecutionSession(test_qasm, backend="classiq/simulator", transpilation_option=TranspilationOption.DECOMPOSE) as session:
            classiq_frame = session.calculate_state_vector(amplitude_threshold=0.0)
        statevector, state_norm_err = dense_classiq_statevector(classiq_frame, 18)
        normalization_error = max(normalization_error, state_norm_err)
        ancilla_error = max(ancilla_error, np.max(np.abs(statevector[logical_size:])))
        basis_phases = np.zeros(logical_size)
        for qubit, phase in enumerate(phases):
            basis_phases += ((basis >> qubit) & 1) * phase
        expected_state = np.zeros(1 << 18, dtype=np.complex128)
        expected_state[:logical_size] = np.exp(1j * basis_phases) / np.sqrt(logical_size) * target_phases
        if test_index == 0:
            overlap = np.vdot(expected_state, statevector)
            shared_global_phase = overlap / abs(overlap)
        max_error = max(max_error, np.max(np.abs(statevector - shared_global_phase * expected_state)))

print(f"Max error:           {max_error:.2e}")
print(f"Ancilla error:       {ancilla_error:.2e}")
print(f"Normalization error: {normalization_error:.2e}")

if max_error < STATE_ERROR_THRESHOLD and ancilla_error < STATE_ERROR_THRESHOLD:
    print("\n>>> ALL VERIFICATION CHECKS PASSED! <<<")
    Path("submission.qasm").write_text(submission_qasm, encoding="utf-8")
    Path("final_best.qasm").write_text(submission_qasm, encoding="utf-8")
    print(f"Updated submission.qasm and final_best.qasm with Depth {metrics.depth}!")
else:
    print("\n>>> VERIFICATION FAILED! <<<")
