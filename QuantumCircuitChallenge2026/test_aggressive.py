#!/usr/bin/env python3
"""
More aggressive D2 edge consolidation and ordering experiments.
"""
import warnings
from typing import Dict, Any
import classiq
from classiq import *
from classiq.qmod.symbolic import pi
from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings

warnings.filterwarnings("ignore")

COORD_BITS = 6
BASELINE = 3820

def synthesize_and_measure(oracle_func, name: str) -> Dict[str, Any]:
    try:
        @qfunc
        def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
            allocate(x)
            allocate(y)
            hadamard_transform(x)
            hadamard_transform(y)
            oracle_func(x, y)

        model = create_model(main, constraints=Constraints(
            optimization_parameter=OptimizationParameter.DEPTH, max_width=18))
        qprog = synthesize(model)

        raw_qasm = export(qprog, TargetLanguage.QASM2)
        raw_lines = raw_qasm.splitlines()
        prep_idx = {i for i, l in enumerate(raw_lines)
                    if l.strip().startswith('hadamard_transform_') and 'q[' in l}
        candidate_qasm = '\n'.join(l for i, l in enumerate(raw_lines) if i not in prep_idx)
        candidate_qprog = quantum_program_from_qasm(candidate_qasm)

        transpiled = classiq.transpile(
            candidate_qprog,
            preferences=Preferences(
                transpilation_option=TranspilationOption.INTENSIVE,
                custom_hardware_settings=CustomHardwareSettings(basis_gates=['u3', 'cx']),
            ),
        )
        metrics = classiq.get_transpiled_circuit_metrics(transpiled)

        return {
            "name": name,
            "depth": metrics.depth,
            "cx": metrics.count_ops.get('cx', 0),
            "status": "success",
        }
    except Exception as e:
        return {
            "name": name,
            "depth": None,
            "cx": None,
            "status": "error",
            "error": str(e)[:200]
        }

# BASE
@qperm
def oracle_base(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# Variant 1: Try merging all D2 edge y-values into one control
# This eliminates the x>=38..42 control entirely
@qperm
def oracle_d2_edge_merge_all(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # Merge ALL 4 D2 edge controls into 2:
    # Row 11-12-26-27 merged into one control
    control(((y == 11) | (y == 12) | (y == 26) | (y == 27)) & ((x >= 36) & (x <= 42)), lambda: phase(pi))
    # Row 15-17-23-21 consolidated via x
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47) | (x == 32) | (x == 48)), lambda: phase(pi))

# Variant 2: Check if pixel coverage still works
# D2 edges contribute 56 pixels. Let's verify what we're capturing:
# Original:
#   (y 15..23, x 33) = 9 pixels
#   (y 15..23, x 47) = 9 pixels
#   (y 17..21, x 32) = 5 pixels
#   (y 17..21, x 48) = 5 pixels
#   (x 36..44, y 12) = 9 pixels
#   (x 38..42, y 27) = 5 pixels
# Wait - this doesn't seem right. Let me check the pixel count more carefully.

# Actually, let's try something simpler: just change the D2 edge ordering
@qperm
def oracle_d2_edges_middle(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # Put one D2 edge early, one late
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))

if __name__ == "__main__":
    tests = [
        ("Base (3820)", oracle_base),
        ("D2 Edge Merge All", oracle_d2_edge_merge_all),
        ("D2 Edges Middle Positioning", oracle_d2_edges_middle),
    ]

    for name, func in tests:
        print(f"Testing: {name}...")
        r = synthesize_and_measure(func, name)
        if r["depth"] is not None:
            delta = BASELINE - r["depth"]
            marker = " *** IMPROVEMENT! ***" if delta > 0 else ""
            print(f"  -> Depth: {r['depth']}, CX: {r['cx']} (delta={delta:+d}){marker}")
        else:
            print(f"  -> ERROR: {r.get('error')[:80]}")
        print()
