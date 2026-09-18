#!/usr/bin/env python3
"""
Comprehensive optimization test suite (Part 2) for Classiq Challenge 2026.
Tests remaining approaches 4-11 beyond the 3,992-depth baseline.
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
BASELINE_DEPTH = 3992
BASELINE_CX = 2645

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
# Current best for reference
# ==============================================================================
@qperm
def oracle_current_best(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
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
# APPROACH 4: Direct u3/cx-Aware Synthesis
# Use CustomHardwareSettings targeting u3/cx directly during synthesis
# ==============================================================================
@qperm
def oracle_direct_basis(x: Const[QNum], y: Const[QNum]) -> None:
    """Same oracle but synthesized with u3/cx in optimization parameter"""
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
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

def test_direct_basis():
    """Test using u3/cx-aware preferences during synthesis"""
    try:
        @qfunc
        def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
            allocate(x)
            allocate(y)
            hadamard_transform(x)
            hadamard_transform(y)
            oracle_direct_basis(x, y)

        # Use different optimization parameters
        model = create_model(main, constraints=Constraints(
            optimization_parameter=OptimizationParameter.DEPTH,
            max_width=18,
            basis_optimization_level=1,  # Try level 1
        ))
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
                custom_hardware_settings=CustomHardwareSettings(
                    basis_gates=['u3', 'cx'],
                    basis_optimization_level=1,
                ),
            ),
        )
        metrics = classiq.get_transpiled_circuit_metrics(transpiled)
        return {
            "name": "Direct U3/CX Basis",
            "width": metrics.width,
            "depth": metrics.depth,
            "cx": metrics.count_ops.get('cx', 0),
            "status": "synthesized (basis_optimization_level=1)"
        }
    except Exception as e:
        return {
            "name": "Direct U3/CX Basis",
            "depth": None,
            "cx": None,
            "status": "error",
            "error": str(e)[:200]
        }

# ==============================================================================
# APPROACH 5: Automated Control-Ordering Search
# Test different orders for applying controls
# ==============================================================================
@qperm
def oracle_order_s_first(x: Const[QNum], y: Const[QNum]) -> None:
    """S-first ordering: Largest region first"""
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

@qperm
def oracle_order_nested_first(x: Const[QNum], y: Const[QNum]) -> None:
    """Nested-region-first: smallest/most-inner regions first"""
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    # D2 inner first, then D1, then Bar, then S
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))

# ==============================================================================
# APPROACH 7: Ancilla/Width Sweep
# Test different width limits: 12, 13, 14, 15, 16, 17, 18
# ==============================================================================
def test_width_sweep():
    """Test current best oracle at different width limits"""
    results = []
    for width in [12, 13, 14, 15, 16, 17, 18]:
        print(f"  Testing width={width}...")
        result = synthesize_and_measure(oracle_current_best, f"Width={width}", width)
        results.append(result)
    return results

# ==============================================================================
# APPROACH 8: Global Y-Symmetry (dy = |y - 41|)
# ==============================================================================
@qperm
def oracle_global_y_sym(x: Const[QNum], y: Const[QNum]) -> None:
    """Exploit y=41 symmetry with distance-from-center"""
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    # S uses dy = |y - 41|, d <= 12
    control(is_S_x & ((y - 41) ** 2 <= 144), lambda: phase(pi))

    # Merged bar+d1-core uses dy <= 2
    control((x >= 27) & (x <= 61) & ((y - 41) ** 2 <= 4), lambda: phase(pi))

    # D1 shells using distance from center
    control((x >= 50) & (x <= 60) & ((y - 41) ** 2 == 9), lambda: phase(pi))  # dy = 3
    control((x >= 51) & (x <= 59) & ((y - 41) ** 2 == 16), lambda: phase(pi))  # dy = 4
    control((x >= 53) & (x <= 57) & ((y - 41) ** 2 == 25), lambda: phase(pi))  # dy = 5
    control((x >= 49) & (x <= 61) & ((y - 41) ** 2 == 0), lambda: phase(pi))   # dy = 0

    # D2 using dy = |y - 19|
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

# ==============================================================================
# APPROACH 9: Distance-from-Centre Disk (Euclidean distance)
# ==============================================================================
@qperm
def oracle_distance_based(x: Const[QNum], y: Const[QNum]) -> None:
    """Use distance squared threshold for disks instead of shells"""
    is_S_x = (x >= 2) & (x <= 26)

    # S complete
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))

    # Merged bar + D1 core
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # D1 using distance formula: (x-55)^2 + (y-41)^2 <= 42
    # This is a single control but requires squaring operations
    # May not synthesize well, but worth testing
    control((x - 55) ** 2 + (y - 41) ** 2 <= 42, lambda: phase(pi))

    # D2 using distance formula: (x-40)^2 + (y-19)^2 <= 72
    control((x - 40) ** 2 + (y - 19) ** 2 <= 72, lambda: phase(pi))

# ==============================================================================
# APPROACH 10: Post-synthesis optimization using Qiskit
# We'll skip actual QASM optimization here and just note the approach
# ==============================================================================
def test_qiskit_optimize_post():
    """Test if Qiskit can optimize the exported QASM further"""
    try:
        from qiskit import QuantumCircuit, transpile as qk_transpile
        from qiskit.converters import circuit_from_qasm

        # Read the submission QASM
        qasm_str = Path("submission.qasm").read_text(encoding="utf-8")
        qc = circuit_from_qasm(qasm_str, edge_look_ahead=10)

        # Apply optimization passes
        optimized_qc = qk_transpile(
            qc,
            basis_gates=['u3', 'cx'],
            optimization_method=3,  # Maximum optimization
            layout_method='dense',
            routing_method='none',
            seed_transpiler=42,
        )

        depth = optimized_qc.depth()
        cx_count = optimized_qc.count_ops().get('cx', 0)

        return {
            "name": "Post-Synthesis Qiskit Opt",
            "width": optimized_qc.num_qubits,
            "depth": depth,
            "cx": cx_count,
            "status": "synthesized"
        }
    except Exception as e:
        return {
            "name": "Post-Synthesis Qiskit Opt",
            "depth": None,
            "cx": None,
            "status": "error",
            "error": str(e)[:200]
        }

# ==============================================================================
# APPROACH 11: BDD/Shannon using manual decomposition
# Represent coordinate bits directly
# ==============================================================================
@qperm
def oracle_boolean_cubes(x: Const[QNum], y: Const[QNum]) -> None:
    """Use direct bit-range checks on coordinate registers"""
    # Instead of arithmetic comparators, try range checks on 2-bit slices
    # x is 6 bits: x[0] is LSB, x[5] is MSB
    # x in [2,26] means x[5:1] in [0, 13] roughly... complex
    # This is a test of whether boolean cube decomposition helps
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # D2 - try using x[5] (bit 5) directly
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
    print("OPTIMIZATION TEST SUITE - PART 2")
    print(f"Baseline: Depth {BASELINE_DEPTH}, CX {BASELINE_CX}")
    print("="*80)
    print()

    # Approach 0: Confirm baseline
    print("[1/9] Testing Current Best (confirmation)...")
    r = synthesize_and_measure(oracle_current_best, "Current Best", 18)
    results.append(r)

    # Approach 4: Direct basis
    print("[2/9] Testing Direct U3/CX Basis...")
    r = test_direct_basis()
    results.append(r)

    # Approach 5: Control ordering
    print("[3/9] Testing Control Ordering - S-first...")
    r = synthesize_and_measure(oracle_order_s_first, "Order: S-first", 18)
    results.append(r)

    print("[4/9] Testing Control Ordering - Nested-first...")
    r = synthesize_and_measure(oracle_order_nested_first, "Order: Nested-first", 18)
    results.append(r)

    # Approach 7: Width sweep
    print("[5/9] Testing Width Sweep (12-18)...")
    width_results = test_width_sweep()
    results.extend(width_results)

    # Approach 8: Global Y-symmetry
    print("[6/9] Testing Global Y-Symmetry (distance from y=41)...")
    r = synthesize_and_measure(oracle_global_y_sym, "Global Y-Symmetry", 18)
    results.append(r)

    # Approach 9: Distance-based disks
    print("[7/9] Testing Distance-based Disk Representation...")
    r = synthesize_and_measure(oracle_distance_based, "Distance-based Disks", 18)
    results.append(r)

    # Approach 10: Qiskit post-optimization
    print("[8/9] Testing Post-Synthesis Qiskit Optimization...")
    r = test_qiskit_optimize_post()
    results.append(r)

    # Approach 11: Boolean cubes
    print("[9/9] Testing Boolean Cube Decomposition...")
    r = synthesize_and_measure(oracle_boolean_cubes, "Boolean Cube Decomp", 18)
    results.append(r)

    print()
    print("="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    for r in results:
        if r["depth"] is not None:
            delta = BASELINE_DEPTH - r["depth"]
            marker = " <-- IMPROVEMENT!" if delta > 0 else ""
            print(f"  {r['name']:40s} D={r['depth']:5d} CX={r['cx']:5d} ({delta:+5d}){marker}")
        else:
            print(f"  {r['name']:40s} ERROR: {r.get('error', 'Unknown')[:60]}")

    Path("optimization_results_part2.json").write_text(json.dumps(results, indent=2))
    print("\nResults saved to optimization_results_part2.json")
