#!/usr/bin/env python3
"""
Test different syntaxes for consolidating D1 outer shells.
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

        # We don't even need transpilation if we just want to see if it synthesizes
        # but let's do it to get depth.
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

# BASE (Depth 3820):
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

# D1 Shell Consolidation using equality (y == 37 | y == 38 | y == 44 | y == 45)
@qperm
def oracle_d1_equality_consolidation(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # Replaced (y>=37 & y<=38) and (y>=44 & y<=45) with exact OR matches
    is_shell1 = (y == 37) | (y == 38) | (y == 44) | (y == 45)
    control(is_shell1 & is_d1_50_60, lambda: phase(pi))

    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# D1 Shell Consolidation using separate AND conditions joined by OR
@qperm
def oracle_d1_range_consolidation(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    is_range1 = (y >= 37) & (y <= 38)
    is_range2 = (y >= 44) & (y <= 45)

    # Let's see if this evaluates successfully:
    control((is_range1 | is_range2) & is_d1_50_60, lambda: phase(pi))

    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

if __name__ == "__main__":
    tests = [
        ("Base D2 X-Consolidated (Depth 3820)", oracle_base),
        ("(y==37|y==38|y==44|y==45)", oracle_d1_equality_consolidation),
        ("(y>=37 & y<=38) | (y>=44 & y<=45)", oracle_d1_range_consolidation)
    ]

    for name, func in tests:
        print(f"Testing: {name}...")
        r = synthesize_and_measure(func, name)
        if r["depth"] is not None:
            print(f"  -> Depth: {r['depth']}, CX: {r['cx']}")
        else:
            print(f"  -> ERROR: {r.get('error')[:80]}")
        print()
