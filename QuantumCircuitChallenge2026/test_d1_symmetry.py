#!/usr/bin/env python3
"""
Test separating Bar from D1 and exploiting D1/D2 disk symmetry.
Key idea: simpler predicates may synthesize shorter even with more controls.
"""
import warnings
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

def test_oracle(oracle_func, name: str):
    @qfunc
    def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
        allocate(x)
        allocate(y)
        hadamard_transform(x)
        hadamard_transform(y)
        oracle_func(x, y)

    try:
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
        print(f"  {name:50s} Depth={metrics.depth:5d} CX={metrics.count_ops.get('cx', 0):5d}")
        return metrics.depth, metrics.count_ops.get('cx', 0)
    except Exception as e:
        print(f"  {name:50s} ERROR: {e}")
        return None, None

# =========================================================================
# STRATEGY A: Current best (11 controls)
# =========================================================================
@qperm
def oracle_current_best(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d2_x_38_42 = (x >= 38) & (x <= 42)
    is_d2_x_36_44 = (x >= 36) & (x <= 44)
    is_d2_x_34_46 = (x >= 34) & (x <= 46)
    is_d2_x_33_47 = (x >= 33) & (x <= 47)
    is_d2_x_32_48 = (x >= 32) & (x <= 48)
    is_d1_x_53_57 = (x >= 53) & (x <= 57)
    is_d1_x_51_59 = (x >= 51) & (x <= 59)
    is_d1_x_50_60 = (x >= 50) & (x <= 60)

    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & is_d2_x_32_48, lambda: phase(pi))
    control((y >= 15) & (y <= 16) & is_d2_x_33_47, lambda: phase(pi))
    control((y >= 22) & (y <= 23) & is_d2_x_33_47, lambda: phase(pi))
    control((y >= 13) & (y <= 14) & is_d2_x_34_46, lambda: phase(pi))
    control((y >= 24) & (y <= 25) & is_d2_x_34_46, lambda: phase(pi))
    control(is_d2_x_36_44 & ((y == 12) | (y == 26)), lambda: phase(pi))
    control(is_d2_x_38_42 & ((y == 11) | (y == 27)), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_x_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_x_50_60, lambda: phase(pi))
    control(is_d1_x_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_x_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

# =========================================================================
# STRATEGY B: Separate Bar from D1
# Bar = original (x=26..49, y=39..43) — 24×5 rectangle
# D1 = full disk approximation (5 y-symmetric controls)
# 14 controls total but possibly simpler predicates
# =========================================================================
@qperm
def oracle_sep_bar_d1(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d2_x_38_42 = (x >= 38) & (x <= 42)
    is_d2_x_36_44 = (x >= 36) & (x <= 44)
    is_d2_x_34_46 = (x >= 34) & (x <= 46)
    is_d2_x_33_47 = (x >= 33) & (x <= 47)
    is_d2_x_32_48 = (x >= 32) & (x <= 48)
    is_d1_x_49_61 = (x >= 49) & (x <= 61)
    is_d1_x_50_60 = (x >= 50) & (x <= 60)
    is_d1_x_51_59 = (x >= 51) & (x <= 59)
    is_d1_x_53_57 = (x >= 53) & (x <= 57)

    # S complete
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))

    # Bar original only (no D1 extension)
    control((x >= 26) & (x <= 49) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # D1 full disk (separated from bar) — 5 symmetric shell controls
    control((y >= 39) & (y <= 43) & is_d1_x_49_61, lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_x_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_x_50_60, lambda: phase(pi))
    control(is_d1_x_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_x_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # D2 unchanged
    control((y >= 17) & (y <= 21) & is_d2_x_32_48, lambda: phase(pi))
    control((y >= 15) & (y <= 16) & is_d2_x_33_47, lambda: phase(pi))
    control((y >= 22) & (y <= 23) & is_d2_x_33_47, lambda: phase(pi))
    control((y >= 13) & (y <= 14) & is_d2_x_34_46, lambda: phase(pi))
    control((y >= 24) & (y <= 25) & is_d2_x_34_46, lambda: phase(pi))
    control(is_d2_x_36_44 & ((y == 12) | (y == 26)), lambda: phase(pi))
    control(is_d2_x_38_42 & ((y == 11) | (y == 27)), lambda: phase(pi))


# =========================================================================
# STRATEGY C: Same as B but consolidate D1 y-mirror pairs
# D1 outer shells consolidated, core separate
# 12 controls total
# =========================================================================
@qperm
def oracle_sep_bar_d1_consol(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d2_x_38_42 = (x >= 38) & (x <= 42)
    is_d2_x_36_44 = (x >= 36) & (x <= 44)
    is_d2_x_34_46 = (x >= 34) & (x <= 46)
    is_d2_x_33_47 = (x >= 33) & (x <= 47)
    is_d2_x_32_48 = (x >= 32) & (x <= 48)
    is_d1_x_49_61 = (x >= 49) & (x <= 61)
    is_d1_x_50_60 = (x >= 50) & (x <= 60)
    is_d1_x_51_59 = (x >= 51) & (x <= 59)
    is_d1_x_53_57 = (x >= 53) & (x <= 57)

    # S complete
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))

    # Bar original only
    control((x >= 26) & (x <= 49) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # D1 core (y=39..43, widest ring)
    control((y >= 39) & (y <= 43) & is_d1_x_49_61, lambda: phase(pi))

    # D1 y-symmetric shells (using existing OR consolidation)
    # d1_x_50_60 used for BOTH y=37,38 and y=44,45
    control((y >= 37) & (y <= 38) & is_d1_x_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_x_50_60, lambda: phase(pi))
    control(is_d1_x_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_x_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # D2 unchanged
    control((y >= 17) & (y <= 21) & is_d2_x_32_48, lambda: phase(pi))
    control((y >= 15) & (y <= 16) & is_d2_x_33_47, lambda: phase(pi))
    control((y >= 22) & (y <= 23) & is_d2_x_33_47, lambda: phase(pi))
    control((y >= 13) & (y <= 14) & is_d2_x_34_46, lambda: phase(pi))
    control((y >= 24) & (y <= 25) & is_d2_x_34_46, lambda: phase(pi))
    control(is_d2_x_36_44 & ((y == 12) | (y == 26)), lambda: phase(pi))
    control(is_d2_x_38_42 & ((y == 11) | (y == 27)), lambda: phase(pi))


# =========================================================================
# STRATEGY D: Also separate D2 symmetry more explicitly
# D2 has perfect symmetry about y=19 - exploit with consolidation
# =========================================================================
@qperm
def oracle_full_disk_symmetry(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_x_49_61 = (x >= 49) & (x <= 61)
    is_d1_x_50_60 = (x >= 50) & (x <= 60)
    is_d1_x_51_59 = (x >= 51) & (x <= 59)
    is_d1_x_53_57 = (x >= 53) & (x <= 57)

    # S complete
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))

    # Bar original only
    control((x >= 26) & (x <= 49) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # D1 core
    control((y >= 39) & (y <= 43) & is_d1_x_49_61, lambda: phase(pi))

    # D1 symmetric shells
    control((y >= 37) & (y <= 38) & is_d1_x_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_x_50_60, lambda: phase(pi))
    control(is_d1_x_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_x_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # D2 with y-symmetry about y=19 more explicitly exploited
    # D2 structure:
    # d=0: y=19, x in [32,48] (center row, widest)
    # d=1,2: y in [17..18, 20..21], x in [32,48]
    # d=3,4: y in [15..16, 22..23], x in [33,47]
    # d=5,6: y in [13..14, 24..25], x in [34,46]
    # d=7: y in [12, 26], x in [36,44]
    # d=8: y in [11, 27], x in [38,42]

    # Combine D2 center (y=17..21) into ONE wide block
    control((y >= 17) & (y <= 21) & (x >= 32) & (x <= 48), lambda: phase(pi))

    # Then symmetric pairs
    control((y >= 15) & (y <= 16) & (x >= 33) & (x <= 47), lambda: phase(pi))
    control((y >= 22) & (y <= 23) & (x >= 33) & (x <= 47), lambda: phase(pi))
    control((y >= 13) & (y <= 14) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 24) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))


# =========================================================================
# STRATEGY E: Merge D2 y-symmetric pairs into single controls
# Reduce D2 from 7 to 5 controls by merging (15-16)+(22-23) and (13-14)+(24-25)
# =========================================================================
@qperm
def oracle_d2_merged(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_x_49_61 = (x >= 49) & (x <= 61)
    is_d1_x_50_60 = (x >= 50) & (x <= 60)
    is_d1_x_51_59 = (x >= 51) & (x <= 59)
    is_d1_x_53_57 = (x >= 53) & (x <= 57)

    # S complete
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))

    # Bar original only
    control((x >= 26) & (x <= 49) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # D1
    control((y >= 39) & (y <= 43) & is_d1_x_49_61, lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_x_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_x_50_60, lambda: phase(pi))
    control(is_d1_x_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_x_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # D2 with more consolidation: merge y-symmetric pairs
    # D2 full block y=13..25, x=32..48 (but overshoot: need to cut edges)
    # Instead: D2 center as one big rectangle
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    # Add extra pixels at wider rows
    control((y >= 15) & (y <= 23) & (x >= 33) & (x <= 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x >= 47) & (x <= 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x >= 32) & (x <= 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x >= 48) & (x <= 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))


# =========================================================================
# STRATEGY F: D2 as complete rectangle + edge corrections
# =========================================================================
@qperm
def oracle_d2_complete_rect(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_x_49_61 = (x >= 49) & (x <= 61)
    is_d1_x_50_60 = (x >= 50) & (x <= 60)
    is_d1_x_51_59 = (x >= 51) & (x <= 59)
    is_d1_x_53_57 = (x >= 53) & (x <= 57)

    # S complete
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))

    # Bar original only
    control((x >= 26) & (x <= 49) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # D1
    control((y >= 39) & (y <= 43) & is_d1_x_49_61, lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_x_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_x_50_60, lambda: phase(pi))
    control(is_d1_x_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_x_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # D2 as one big rectangle + corrections
    # Core: y=11..27, x=38..42 (smallest ring, biggest y-range)
    control((y >= 11) & (y <= 27) & (x >= 38) & (x <= 42), lambda: phase(pi))

    # Extension: y=12..26, x=36..37 and x=43..44
    control((y >= 12) & (y <= 26) & (x >= 36) & (x <= 37), lambda: phase(pi))
    control((y >= 12) & (y <= 26) & (x >= 43) & (x <= 44), lambda: phase(pi))

    # Extension: y=13..25, x=34..35 and x=45..46
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 35), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 45) & (x <= 46), lambda: phase(pi))

    # Extension: y=15..23, x=33 and x=47
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))

    # Extension: y=17..21, x=32 and x=48
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))


# =========================================================================
# STRATEGY G: D2 as complete rectangle + x-symmetric edge corrections
# Merge symmetric x edges into single controls using x-OR
# =========================================================================
@qperm
def oracle_d2_xsym(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_x_49_61 = (x >= 49) & (x <= 61)
    is_d1_x_50_60 = (x >= 50) & (x <= 60)
    is_d1_x_51_59 = (x >= 51) & (x <= 59)
    is_d1_x_53_57 = (x >= 53) & (x <= 57)

    # S complete
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))

    # Bar original only
    control((x >= 26) & (x <= 49) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # D1
    control((y >= 39) & (y <= 43) & is_d1_x_49_61, lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_x_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_x_50_60, lambda: phase(pi))
    control(is_d1_x_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_x_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # D2 exploiting BOTH x-symmetry (about x=40) and y-symmetry (about y=19)
    # Core: y=11..27, x=38..42 (innermost ring)
    control((y >= 11) & (y <= 27) & (x >= 38) & (x <= 42), lambda: phase(pi))

    # Symmetric x-extensions using OR on x-values
    # x=36,37 and x=43,44 => can combine with shared y
    control((y >= 12) & (y <= 26) & ((x == 36) | (x == 44)), lambda: phase(pi))
    control((y >= 12) & (y <= 26) & ((x == 37) | (x == 43)), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & ((x == 34) | (x == 46)), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & ((x == 35) | (x == 45)), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))


if __name__ == "__main__":
    print("=" * 75)
    print("DISK SYMMETRY EXPLOITATION TESTS")
    print("=" * 75)
    print()

    results = []
    results.append(("Current Best (11 controls)", *test_oracle(oracle_current_best, "Current Best (11 controls)")))
    results.append(("Sep Bar + D1 full (14 controls)", *test_oracle(oracle_sep_bar_d1, "Sep Bar + D1 full (14 controls)")))
    results.append(("Sep Bar + D1 consol (12 controls)", *test_oracle(oracle_sep_bar_d1_consol, "Sep Bar + D1 consol (12 controls)")))
    results.append(("Full disk symmetry (14 controls)", *test_oracle(oracle_full_disk_symmetry, "Full disk symmetry (14 controls)")))
    results.append(("D2 merged pairs (14 controls)", *test_oracle(oracle_d2_merged, "D2 merged pairs (14 controls)")))
    results.append(("D2 complete rect (16 controls)", *test_oracle(oracle_d2_complete_rect, "D2 complete rect (16 controls)")))
    results.append(("D2 x-symmetry OR (14 controls)", *test_oracle(oracle_d2_xsym, "D2 x-symmetry OR (14 controls)")))

    print("\n" + "=" * 75)
    print("SUMMARY")
    print("=" * 75)
    valid = [(n, d, c) for n, d, c in results if d is not None]
    for name, depth, cx in sorted(valid, key=lambda x: (x[1], x[2])):
        delta = 4361 - depth
        marker = " <-- NEW BEST!" if delta > 0 else ""
        print(f"  {name:45s} Depth={depth:5d} CX={cx:5d} ({delta:+5d}){marker}")
