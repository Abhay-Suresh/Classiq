#!/usr/bin/env python3
"""
Standalone verification script for the champion submission.qasm (Depth 2,959 | CX 1,948).
Tests 3 random product-phase superpositions across all 4,096 basis coordinates.
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

def dense_classiq_statevector(frame, width: int):
    statevector = np.zeros(1 << width, dtype=np.complex128)
    for row in frame.itertuples(index=False):
        bitstring = str(row.bitstring).replace(" ", "")
        statevector[int(bitstring, 2)] = complex(row.amplitude)
    normalization_error = abs(np.vdot(statevector, statevector).real - 1)
    return statevector, normalization_error

if __name__ == "__main__":
    qasm_path = Path("submission.qasm")
    if not qasm_path.exists():
        raise FileNotFoundError("submission.qasm not found!")

    submission_source = qasm_path.read_text(encoding="utf-8")
    logical_size = GRID_SIZE ** 2
    submission_width = 18

    # Extract metrics
    qprog = quantum_program_from_qasm(submission_source)
    metrics = classiq.get_transpiled_circuit_metrics(qprog)
    print(f"Verifying submission.qasm:")
    print(f"  Width:    {metrics.width}")
    print(f"  Depth:    {metrics.depth}")
    print(f"  CX count: {metrics.count_ops.get('cx', 0)}")

    STATE_ERROR_THRESHOLD = 1e-10
    rng = np.random.default_rng(42)
    random_phases = rng.uniform(-np.pi, np.pi, size=(3, 2 * COORD_BITS))
    target_phases = np.array(
        [-1 if logo_pixel(x, y) else 1 for y in range(GRID_SIZE) for x in range(GRID_SIZE)],
        dtype=np.complex128,
    )

    source_without_comments = re.sub(r"//[^\n]*", lambda m: " " * len(m.group()), submission_source)
    qreg_matches = list(re.finditer(rf"\bqreg\s+q\s*\[\s*{submission_width}\s*\]\s*;", source_without_comments))
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
            statevector, state_norm_err = dense_classiq_statevector(classiq_frame, submission_width)
            normalization_error = max(normalization_error, state_norm_err)
            ancilla_error = max(ancilla_error, np.max(np.abs(statevector[logical_size:])))
            basis_phases = np.zeros(logical_size)
            for qubit, phase in enumerate(phases):
                basis_phases += ((basis >> qubit) & 1) * phase
            expected_state = np.zeros(1 << submission_width, dtype=np.complex128)
            expected_state[:logical_size] = np.exp(1j * basis_phases) / np.sqrt(logical_size) * target_phases
            if test_index == 0:
                overlap = np.vdot(expected_state, statevector)
                shared_global_phase = overlap / abs(overlap)
            max_error = max(max_error, np.max(np.abs(statevector - shared_global_phase * expected_state)))

    print(f"\nVerification results:")
    print(f"  Max error:           {max_error:.2e}")
    print(f"  Ancilla error:       {ancilla_error:.2e}")
    print(f"  Normalization error: {normalization_error:.2e}")

    if max_error < STATE_ERROR_THRESHOLD and ancilla_error < STATE_ERROR_THRESHOLD:
        print("\n>>> ALL VERIFICATION CHECKS PASSED! <<<")
    else:
        print("\n>>> VERIFICATION FAILED! <<<")
