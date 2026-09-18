#!/usr/bin/env python3
"""
Alternative D1 approaches:
1. Reorder D1 shells (largest shell first)
2. Consolidate y==36|46 and y==35|47 into single control
3. Try different control insertion points
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

# BASE (Depth 3820)
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

# Variant 1: Merge the two middle shells (y==36/46 and y==35/47) — try single x-range
@qperm
def oracle_d1_merge_middle_shells(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))

    # Try merging middle shells with wider x-range:
    control(((y == 36) | (y == 46) | (y == 35) | (y == 47)) & ((x >= 51) & (x <= 59)), lambda: phase(pi))

    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# Variant 2: D1 shells ordered from innermost to outermost
@qperm
def oracle_d1_reverse_order(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # Reverse: innermost (53-57) first, outermost (50-60) last
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))

    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# Variant 3: Interleave D1 and D2 edge controls
@qperm
def oracle_interleaved_d1_d2(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # Alternate D1 and D2 edge controls
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# Variant 4: D2 edges first before D1 shells
@qperm
def oracle_d2_edges_first(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # D2 edges completely first
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

    # Then D1 shells
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

if __name__ == "__main__":
    print(f"Baseline: Depth {BASELINE}")
    print("="*80)

    tests = [
        ("Base (3820)", oracle_base),
        ("D1 Middle Shells Merged", oracle_d1_merge_middle_shells),
        ("D1 Reverse Order (innermost first)", oracle_d1_reverse_order),
        ("Interleaved D1/D2 Edges", oracle_interleaved_d1_d2),
        ("D2 Edges First, Then D1", oracle_d2_edges_first),
    ]

    for name, func in tests:
        print(f"\nTesting: {name}...")
        r = synthesize_and_measure(func, name)
        if r["depth"] is not None:
            delta = BASELINE - r["depth"]
            marker = " *** IMPROVEMENT! ***" if delta > 0 else ""
            print(f"  -> Depth: {r['depth']}, CX: {r['cx']} (delta={delta:+d}){marker}")
        else:
            print(f"  -> ERROR: {r.get('error')[:80]}")
