#!/usr/bin/env python3
"""
Correct ancilla-based approach using within_apply.
"""

import numpy as np
from pathlib import Path

import classiq
from classiq import *
from classiq.qmod.symbolic import pi
from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings

GRID_SIZE = 64
COORD_BITS = 6

def logo_pixel(x: int, y: int) -> bool:
    """Return True exactly for black pixel (x, y)."""
    return (
        (2 <= x <= 26 and 29 <= y <= 53)
        or (26 <= x <= 49 and 39 <= y <= 43)
        or (x - 55) ** 2 + (y - 41) ** 2 <= 42
        or (x - 40) ** 2 + (y - 19) ** 2 <= 72
    )

@qperm
def logo_phase_oracle(x: Const[QNum], y: Const[QNum]) -> None:
    """
    Try direct control without ancillas - maybe Classiq can handle
    separate range checks better if we structure them differently.
    """
    # Pre-compute shared X conditions
    is_S_x = (x >= 2) & (x <= 26)

    is_d2_x_38_42 = (x >= 38) & (x <= 42)
    is_d2_x_36_44 = (x >= 36) & (x <= 44)
    is_d2_x_34_46 = (x >= 34) & (x <= 46)
    is_d2_x_33_47 = (x >= 33) & (x <= 47)
    is_d2_x_32_48 = (x >= 32) & (x <= 48)

    is_d1_x_53_57 = (x >= 53) & (x <= 57)
    is_d1_x_51_59 = (x >= 51) & (x <= 59)
    is_d1_x_50_60 = (x >= 50) & (x <= 60)

    # Bar (largest, do first)
    control((x >= 2) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # Square S
    control(is_S_x & (y >= 29) & (y <= 38), lambda: phase(pi))
    control(is_S_x & (y >= 44) & (y <= 53), lambda: phase(pi))

    # D2 Circle
    control((y >= 17) & (y <= 21) & is_d2_x_32_48, lambda: phase(pi))

    # Try: Combine y-ranges as a single larger range
    # D2: y=15-16 or y=22-23 can be thought of as:
    #   (y >= 15) & (y <= 16) | (y >= 22) & (y <= 23)
    # But we can't use OR directly...
    #
    # Alternative: Create TWO separate controls, but with a COMBINED condition
    # that checks if y is in either range by using nested conditions

    # This still uses separate controls but structures differently
    control((y >= 15) & (y <= 16) & is_d2_x_33_47, lambda: phase(pi))
    control((y >= 22) & (y <= 23) & is_d2_x_33_47, lambda: phase(pi))
    control((y >= 13) & (y <= 14) & is_d2_x_34_46, lambda: phase(pi))
    control((y >= 24) & (y <= 25) & is_d2_x_34_46, lambda: phase(pi))

    # D2 single y-values (can use OR safely)
    control(is_d2_x_36_44 & ((y == 12) | (y == 26)), lambda: phase(pi))
    control(is_d2_x_38_42 & ((y == 11) | (y == 27)), lambda: phase(pi))

    # D1 Circle
    control((y >= 37) & (y <= 38) & is_d1_x_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_x_50_60, lambda: phase(pi))
    control(is_d1_x_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_x_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

@qfunc
def main(
    x: Output[QNum[COORD_BITS]],
    y: Output[QNum[COORD_BITS]],
) -> None:
    allocate(x)
    allocate(y)
    hadamard_transform(x)
    hadamard_transform(y)
    logo_phase_oracle(x, y)

print("=" * 80)
print("BASELINE VERIFICATION")
print("=" * 80)
print()
print("This is our current best configuration with single y-value consolidation")
print()

baseline = 5329
expected_best = 4959

print("Compiling...")
constraints = Constraints(
    optimization_parameter=OptimizationParameter.DEPTH,
    max_width=18,
)

model = create_model(main, constraints=constraints)
qprog = synthesize(model)
print("Synthesis complete")

# Extract and transpile
raw_qasm = export(qprog, TargetLanguage.QASM2)
raw_lines = raw_qasm.splitlines()

preparation_indices = {
    i for i, line in enumerate(raw_lines)
    if line.lstrip().startswith("hadamard_transform_") and "q[" in line
}

if len(preparation_indices) == 2:
    candidate_qasm = "\n".join(
        line for i, line in enumerate(raw_lines)
        if i not in preparation_indices
    )
    candidate_qprog = quantum_program_from_qasm(candidate_qasm)

    transpiled = classiq.transpile(
        candidate_qprog,
        preferences=Preferences(
            transpilation_option=TranspilationOption.AUTO_OPTIMIZE,
            custom_hardware_settings=CustomHardwareSettings(basis_gates=["u3", "cx"]),
        ),
    )

    metrics = classiq.get_transpiled_circuit_metrics(transpiled)

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Width:    {metrics.width}")
    print(f"Depth:    {metrics.depth}")
    print(f"CX count: {metrics.count_ops.get('cx', 0)}")
    print()

    improvement = baseline - metrics.depth
    improvement_pct = (improvement / baseline) * 100

    print("STATUS")
    print("-" * 80)
    print(f"Baseline:         {baseline}")
    print(f"Expected best:    {expected_best}")
    print(f"Current result:   {metrics.depth}")
    print(f"Total improvement: {improvement:+d} ({improvement_pct:+.2f}%)")
    print()

    if metrics.depth == expected_best:
        print("[CONFIRMED] This is our best solution: 4,959 depth")
        print()
        print("CONCLUSION:")
        print("-" * 80)
        print("We CANNOT consolidate y-range pairs without complex syntax.")
        print()
        print("What works:")
        print("  - Single y-value consolidation: (y==12) | (y==26)")
        print("  - Saves 4 controls, reduces depth by 275 points")
        print()
        print("What doesn't work:")
        print("  - Y-range consolidation: (y>=15 & y<=16) | (y>=22 & y<=23)")
        print("  - Classiq rejects complex boolean expressions")
        print("  - Ancilla syntax is complex and may not help")
        print()
        print("Final Best: 4,959 depth (6.94% improvement over baseline)")
    else:
        print(f"Result differs from expected: {metrics.depth} vs {expected_best}")

    # Save
    submission_qasm = export(
        transpiled,
        TargetLanguage.QASM2,
        transpilation_config=TranspilationConfig(basis_gates=["u3", "cx"]),
    )
    Path("final_best.qasm").write_text(submission_qasm, encoding="utf-8")
    print("Saved to final_best.qasm")
else:
    print("ERROR: Could not extract oracle")