#!/usr/bin/env python3
"""
D2 merged pairs oracle with pixel-perfect boundary handling.
Bar: x=27..48 (avoids overlap with S at x=26 and D1 at x=49)
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
def oracle_d2_merged_fixed(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_x_49_61 = (x >= 49) & (x <= 61)
    is_d1_x_50_60 = (x >= 50) & (x <= 60)
    is_d1_x_51_59 = (x >= 51) & (x <= 59)
    is_d1_x_53_57 = (x >= 53) & (x <= 57)

    # S complete
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))

    # Bar original only (FIXED: 27..48 to avoid overlaps)
    control((x >= 27) & (x <= 48) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # D1
    control((y >= 39) & (y <= 43) & is_d1_x_49_61, lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_x_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_x_50_60, lambda: phase(pi))
    control(is_d1_x_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_x_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # D2 with merged pairs (exploiting y-symmetry about y=19)
    # Core: y=13..25, x=34..46
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))

    # Edge columns (using OR to combine symmetric pairs)
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))


print("Synthesizing D2 merged pairs (fixed)...")
@qfunc
def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
    allocate(x)
    allocate(y)
    hadamard_transform(x)
    hadamard_transform(y)
    oracle_d2_merged_fixed(x, y)

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

# Save
submission_qasm = export(
    transpiled,
    TargetLanguage.QASM2,
    transpilation_config=TranspilationConfig(
        transpilation_level=TranspilationOption.INTENSIVE,
        basis_gates=['u3', 'cx'],
    ),
)
Path("submission.qasm").write_text(submission_qasm, encoding="utf-8")
Path("final_best.qasm").write_text(submission_qasm, encoding="utf-8")
print("Saved to submission.qasm and final_best.qasm")

# Quick verification with 2 random states
print("\nQuick verification...")
target_phases = np.array(
    [-1 if logo_pixel(x, y) else 1 for y in range(GRID_SIZE) for x in range(GRID_SIZE)],
    dtype=np.complex128,
)
logical_size = GRID_SIZE ** 2
rng = np.random.default_rng(42)

for test_index in range(2):
    phases = rng.uniform(-np.pi, np.pi, size=(2 * COORD_BITS))
    basis = np.arange(logical_size, dtype=np.uint16)
    basis_phases = np.zeros(logical_size)
    for qubit, phase in enumerate(phases):
        basis_phases += ((basis >> qubit) & 1) * phase

    prep = [f"u3(pi/2,{p:.17g},0) q[{q}];" for q, p in enumerate(phases)]
    test_qasm = candidate_qasm + "\n" + "\n".join(prep)

    with ExecutionSession(test_qasm, backend="classiq/simulator",
                          transpilation_option=TranspilationOption.DECOMPOSE) as session:
        frame = session.calculate_state_vector(amplitude_threshold=0.0)

    sv = np.zeros(1 << 18, dtype=np.complex128)
    for row in frame.itertuples(index=False):
        bs = str(row.bitstring).replace(" ", "")
        sv[int(bs, 2)] = complex(row.amplitude)

    expected = np.zeros(1 << 18, dtype=np.complex128)
    expected[:logical_size] = np.exp(1j * basis_phases) / np.sqrt(logical_size) * target_phases
    overlap = np.vdot(expected, sv)
    shared_gp = overlap / abs(overlap) if abs(overlap) > 1e-12 else 0
    err = np.max(np.abs(sv - shared_gp * expected))
    anc_err = np.max(np.abs(sv[logical_size:], ))
    print(f"  Test {test_index+1}: max_err={err:.2e}, anc_err={anc_err:.2e}")

print(f"\nFinal: Depth={metrics.depth}, CX={metrics.count_ops.get('cx', 0)}")
