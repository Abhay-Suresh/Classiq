#!/usr/bin/env python3
"""
Test permutations and further consolidations of the 10-Control Hybrid model.
Tests:
1. S -> D2 Core -> Merged Bar+D1 -> D1 shells -> D2 edges
2. Interleaved S, D2, D1 orderings
3. True 10-control / 9-control with D2 x-symmetry consolidation ((x==33) | (x==47)), ((x==32) | (x==48))
4. D1 shell consolidation
"""
import warnings
import json
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import classiq
from classiq import *
from classiq.qmod.symbolic import pi
from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings

warnings.filterwarnings("ignore")

COORD_BITS = 6
GRID_SIZE = 64
BASELINE_DEPTH = 3960
BASELINE_CX = 2644

def logo_pixel(x: int, y: int) -> bool:
    return (
        (2 <= x <= 26 and 29 <= y <= 53)
        or (26 <= x <= 49 and 39 <= y <= 43)
        or (x - 55) ** 2 + (y - 41) ** 2 <= 42
        or (x - 40) ** 2 + (y - 19) ** 2 <= 72
    )

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
            "width": metrics.width,
            "depth": metrics.depth,
            "cx": metrics.count_ops.get('cx', 0),
            "status": "success",
            "transpiled": transpiled
        }
    except Exception as e:
        return {
            "name": name,
            "width": 18,
            "depth": None,
            "cx": None,
            "status": "error",
            "error": str(e)[:200]
        }

# --- ORACLE VARIANT 1: S -> D2 Core -> Bar+D1 -> D1 shells -> D2 edges ---
@qperm
def oracle_s_d2_bar_d1(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    # S -> D2 Core -> Bar+D1
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # D1 shells
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # D2 edges
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# --- ORACLE VARIANT 2: Interleaved (S -> Bar+D1 -> D1 shells -> D2 Core -> D2 edges) ---
@qperm
def oracle_interleaved_d1_first(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    # S -> Bar+D1 -> all D1 shells (complete D1 before starting D2)
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # Then D2 complete: core -> edges
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# --- ORACLE VARIANT 3: Interleaved D2 first (S -> D2 Core -> D2 edges -> Bar+D1 -> D1 shells) ---
@qperm
def oracle_interleaved_d2_first(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    # S
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))

    # D2 complete: core -> edges
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

    # Bar+D1 -> D1 shells
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

# --- ORACLE VARIANT 4: D2 X-Consolidation (combining x=33|47 and x=32|48) ---
@qperm
def oracle_d2_x_consolidated(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    # 1. Largest regions
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))

    # 2. D1 shells
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # 3. D2 consolidated edges (11 controls total!)
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# --- ORACLE VARIANT 5: D2 X-Consolidated + D2 core first ---
@qperm
def oracle_d2_x_consolidated_d2_first(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    # S -> D2 Core -> Bar+D1
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # D1 shells
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # D2 consolidated edges
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# --- ORACLE VARIANT 6: Full Consolidation (D1 shells + D2 edges) ---
@qperm
def oracle_full_consolidation(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    # 1. Largest regions
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))

    # 2. D1 shells: consolidate 37..38 and 44..45
    control((((y >= 37) & (y <= 38)) | ((y >= 44) & (y <= 45))) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # 3. D2 consolidated edges
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

if __name__ == "__main__":
    print("="*80)
    print("TESTING PERMUTATIONS & CONSOLIDATIONS OF 10-CONTROL HYBRID")
    print(f"Current Best Baseline: Depth {BASELINE_DEPTH}, CX {BASELINE_CX}")
    print("="*80)
    print()

    tests = [
        ("S -> D2 Core -> Bar+D1 -> Shells", oracle_s_d2_bar_d1),
        ("Interleaved (D1 Complete First)", oracle_interleaved_d1_first),
        ("Interleaved (D2 Complete First)", oracle_interleaved_d2_first),
        ("D2 X-Consolidated ((x=33|47), (x=32|48))", oracle_d2_x_consolidated),
        ("D2 X-Consolidated + D2 Core First", oracle_d2_x_consolidated_d2_first),
        ("Full Consolidation (10 controls total)", oracle_full_consolidation),
    ]

    results = []
    best_result = None
    best_depth = BASELINE_DEPTH

    for name, func in tests:
        print(f"Testing: {name}...")
        r = synthesize_and_measure(func, name)
        results.append(r)
        if r["depth"] is not None:
            delta = BASELINE_DEPTH - r["depth"]
            marker = " *** NEW RECORD! ***" if delta > 0 else ""
            print(f"  -> Depth: {r['depth']}, CX: {r['cx']} (delta: {delta:+d}){marker}")
            if r["depth"] < best_depth:
                best_depth = r["depth"]
                best_result = r
        else:
            print(f"  -> ERROR: {r.get('error')[:80]}")
        print()

    print("="*80)
    print("SUMMARY")
    print("="*80)
    for r in results:
        if r["depth"] is not None:
            delta = BASELINE_DEPTH - r["depth"]
            marker = " <-- IMPROVEMENT!" if delta > 0 else ""
            print(f"  {r['name']:45s} D={r['depth']:5d} CX={r['cx']:5d} ({delta:+5d}){marker}")
        else:
            print(f"  {r['name']:45s} ERROR: {r.get('error', '')[:50]}")
