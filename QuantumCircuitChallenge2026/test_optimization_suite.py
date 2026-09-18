#!/usr/bin/env python3
"""
Comprehensive optimization test suite for Classiq Challenge 2026.
Tests 11 advanced approaches beyond the current 4,312-depth baseline.
"""
import warnings
import json
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import classiq
from classiq import *
from classiq.qmod.symbolic import pi
from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings

warnings.filterwarnings("ignore")

COORD_BITS = 6
GRID_SIZE = 64

def logo_pixel(x: int, y: int) -> bool:
    return (
        (2 <= x <= 26 and 29 <= y <= 53)
        or (26 <= x <= 49 and 39 <= y <= 43)
        or (x - 55) ** 2 + (y - 41) ** 2 <= 42
        or (x - 40) ** 2 + (y - 19) ** 2 <= 72
    )

def synthesize_and_measure(oracle_func, name: str, width: int = 18) -> Dict[str, Any]:
    """Synthesize, transpile, measure depth/CX."""
    try:
        @qfunc
        def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
            allocate(x)
            allocate(y)
            hadamard_transform(x)
            hadamard_transform(y)
            oracle_func(x, y)

        model = create_model(main, constraints=Constraints(
            optimization_parameter=OptimizationParameter.DEPTH, max_width=width))
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
            "width": metrics.width,
            "depth": metrics.depth,
            "cx": metrics.count_ops.get('cx', 0),
            "status": "synthesized"
        }
    except Exception as e:
        return {
            "name": name,
            "width": width,
            "depth": None,
            "cx": None,
            "status": "error",
            "error": str(e)[:200]
        }

# ==============================================================================
# APPROACH 0: Current Best (Baseline)
# ==============================================================================
@qperm
def oracle_current_best(x: Const[QNum], y: Const[QNum]) -> None:
    """Current best: S-complete + Bar(27-48) + D1 + D2-merged"""
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_49_61 = (x >= 49) & (x <= 61)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 48) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 39) & (y <= 43) & is_d1_49_61, lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# ==============================================================================
# APPROACH 1: 10-Control Hybrid (Merge Bar + D1 Core)
# ==============================================================================
@qperm
def oracle_10_control_hybrid(x: Const[QNum], y: Const[QNum]) -> None:
    """Merge Bar (27-48) and D1-core (49-61) into one rectangle (27-61, 39-43)"""
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))  # MERGED
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# ==============================================================================
# APPROACH 2: XOR/ESOP Representation (Intentional Overlaps)
# ==============================================================================
@qperm
def oracle_xor_esop(x: Const[QNum], y: Const[QNum]) -> None:
    """Use overlapping rectangles that XOR (phase × phase = 1) to simplify"""
    # Cover entire upper region with large rectangles, let XOR cancel
    control((x >= 2) & (x <= 61) & (y >= 29) & (y <= 53), lambda: phase(pi))
    # Subtract middle gap (x=27-61, y=44-53 NOT in Bar)
    control((x >= 27) & (x <= 61) & (y >= 44) & (y <= 53), lambda: phase(pi))
    # Subtract bottom gap (x=27-48, y=29-38 NOT in S or Bar)
    control((x >= 27) & (x <= 48) & (y >= 29) & (y <= 38), lambda: phase(pi))
    # D1 outer shells
    control((y == 35) & (x >= 53) & (x <= 57), lambda: phase(pi))
    control((y == 47) & (x >= 53) & (x <= 57), lambda: phase(pi))
    control((y == 36) & (x >= 51) & (x <= 59), lambda: phase(pi))
    control((y == 46) & (x >= 51) & (x <= 59), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & (x >= 50) & (x <= 60), lambda: phase(pi))
    control((y >= 44) & (y <= 45) & (x >= 50) & (x <= 60), lambda: phase(pi))
    # D2
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# ==============================================================================
# APPROACH 3: Shared Predicate Tree
# ==============================================================================
@qperm
def oracle_shared_predicate_tree(x: Const[QNum], y: Const[QNum]) -> None:
    """Hierarchical predicate sharing for nested x-intervals"""
    is_S_x = (x >= 2) & (x <= 26)

    # D1 hierarchy: compute once, reuse
    is_d1_base = (x >= 49)
    is_d1_61 = is_d1_base & (x <= 61)
    is_d1_60 = is_d1_base & (x <= 60)
    is_d1_59 = is_d1_base & (x <= 59)
    is_d1_57 = is_d1_base & (x <= 57)

    is_d1_50 = (x >= 50)
    is_d1_50_60 = is_d1_50 & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 48) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 39) & (y <= 43) & is_d1_61, lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# ==============================================================================
# Main test runner
# ==============================================================================
if __name__ == "__main__":
    results = []

    print("="*80)
    print("OPTIMIZATION TEST SUITE")
    print("="*80)
    print()

    # Approach 0
    print("[0/11] Testing Current Best (4,312 baseline)...")
    results.append(synthesize_and_measure(oracle_current_best, "Current Best", 18))

    # Approach 1
    print("[1/11] Testing 10-Control Hybrid...")
    results.append(synthesize_and_measure(oracle_10_control_hybrid, "10-Control Hybrid", 18))

    # Approach 2
    print("[2/11] Testing XOR/ESOP...")
    results.append(synthesize_and_measure(oracle_xor_esop, "XOR/ESOP", 18))

    # Approach 3
    print("[3/11] Testing Shared Predicate Tree...")
    results.append(synthesize_and_measure(oracle_shared_predicate_tree, "Shared Predicate Tree", 18))

    print()
    print("="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    for r in results:
        if r["depth"] is not None:
            delta = 4312 - r["depth"]
            marker = " <-- IMPROVEMENT!" if delta > 0 else ""
            print(f"  {r['name']:30s} Depth={r['depth']:5d} CX={r['cx']:5d} ({delta:+5d}){marker}")
        else:
            print(f"  {r['name']:30s} ERROR: {r.get('error', 'Unknown')[:60]}")

    # Save results
    Path("optimization_results_part1.json").write_text(json.dumps(results, indent=2))
    print("\nResults saved to optimization_results_part1.json")
