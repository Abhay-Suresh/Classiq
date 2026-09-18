# Classiq Quantum Circuit Challenge 2026 - Final Report

**Date:** 2026-09-18  
**Challenge:** Quantum Phase Oracle for 64×64 Classiq Logo

---

## Final Verified Results

### Circuit Metrics
- **Depth:** 4,632
- **CX Count:** 3,126
- **Width:** 18 qubits (12 coordinates + 6 ancillas)
- **Basis Gates:** u3, cx only

### Verification Status
✅ **PASSED** - All correctness checks verified
- Max error: 3.1 × 10⁻¹⁶
- Ancilla error: 5.3 × 10⁻¹⁷
- Normalization error: 2.5 × 10⁻¹⁴
- Random test states: 3 superpositions
- All 1,097 black pixels correctly marked with -1 phase
- All 2,999 white pixels correctly left unchanged

---

## Optimization Journey

### Baseline (Starting Point)
- **Depth:** 5,329
- **CX Count:** 3,502
- **Strategy:** 18 independent rectangle checks with AUTO_OPTIMIZE transpilation

### Optimization 1: X-Predicate Sharing + Control Reordering
- **Depth:** 5,234 (95 point improvement)
- **CX Count:** 3,492
- **Strategy:** Pre-compute 9 shared X-interval predicates, order controls by pixel count (largest first)

### Optimization 2: Single Y-Value Consolidation
- **Depth:** 4,959 (370 point improvement from baseline)
- **CX Count:** 3,312
- **Strategy:** Combine symmetric single-row checks using bitwise OR (e.g., `(y == 12) | (y == 26)`), reducing control count from 18 to 12

### Optimization 3: INTENSIVE Transpilation
- **Depth:** 4,632 (697 point improvement from baseline, **13.08%**)
- **CX Count:** 3,126
- **Strategy:** Use `TranspilationOption.INTENSIVE` instead of `AUTO_OPTIMIZE` for heavier gate optimization passes

---

## Key Technical Discoveries

### 1. Transpilation Configuration Critical Path
The most important discovery was that `export()` must preserve the transpilation level:

```python
# WRONG - Reverts to AUTO_OPTIMIZE during export
submission_qasm = export(
    transpiled,
    TargetLanguage.QASM2,
    transpilation_config=TranspilationConfig(basis_gates=['u3', 'cx'])
)

# CORRECT - Preserves INTENSIVE optimization
submission_qasm = export(
    transpiled,
    TargetLanguage.QASM2,
    transpilation_config=TranspilationConfig(
        transpilation_level=TranspilationOption.INTENSIVE,
        basis_gates=['u3', 'cx']
    )
)
```

This single change recovered 327 depth points (4,959 → 4,632).

### 2. Predicate Sharing Strategy
Pre-computing shared X-conditions reduced redundant comparator synthesis:

```python
# 9 shared X-predicates used across 12 control statements
is_S_x = (x >= 2) & (x <= 26)
is_d2_x_32_48 = (x >= 32) & (x <= 48)
# ... etc
```

### 3. Control Consolidation with Bitwise OR
Classical OR (`|`) on quantum predicates enabled control reduction:

```python
# Before: 2 separate controls
control(is_d2_x_36_44 & (y == 12), lambda: phase(pi))
control(is_d2_x_36_44 & (y == 26), lambda: phase(pi))

# After: 1 consolidated control
control(is_d2_x_36_44 & ((y == 12) | (y == 26)), lambda: phase(pi))
```

Reduced control count from 18 to 12 (6 consolidations).

### 4. Control Ordering Optimization
Ordering controls by pixel count (largest regions first) improved synthesis efficiency, though the exact mechanism is not fully understood.

---

## Unexplored Optimization Directions

The following strategies were identified but not successfully implemented due to time/tooling constraints:

1. **Y-Predicate Sharing:** Attempted but failed verification due to overlapping phase logic with Square S
2. **Boolean Decomposition (BDD/ESOP):** Requires external tools (ABC, Espresso)
3. **Row-First Classification:** More complex predicate structure, unclear benefit
4. **Geometric Symmetry:** Logo has no obvious symmetry to exploit
5. **Aggressive Ancilla Trading:** Limited by 6-ancilla budget, unclear recomputation benefit

---

## Files

### Submission Files
- `submission.qasm` - Verified transpiled circuit (depth 4,632)
- `final_best.qasm` - Backup copy of submission
- `submission.qmod` - Qmod source (for reproducibility)

### Documentation
- `classiq-challenge-baseline (1).ipynb` - Updated challenge notebook with verified results
- `FINAL_REPORT.md` - This document

### Utilities (Kept for Reference)
- `verify_best_solution.py` - Standalone verification script
- `final_summary.py` - Metrics summary script

---

## Submission Checklist

✅ Circuit width ≤ 18 qubits  
✅ Basis gates: u3, cx only  
✅ Coordinates preserved (x, y unchanged)  
✅ Ancillas returned to |0⟩  
✅ Correct phase pattern (-1 on black pixels, +1 on white pixels)  
✅ Global phase independent of coordinates  
✅ Depth: 4,632  
✅ CX count: 3,126  

---

## Competition Context

- **Baseline provided:** 5,329 depth
- **Our improvement:** 697 points (13.08% reduction)
- **Ranking metric:** Depth (primary), CX count (tiebreaker), submission time (second tiebreaker)

---

## Recommendations for Future Work

1. **Investigate Y-sharing more carefully:** The overlap with Square S needs explicit handling
2. **Explore BDD/ESOP tools:** May unlock significant further reduction
3. **Profile transpilation:** Understanding why INTENSIVE outperforms AUTO_OPTIMIZE by 327 points could guide further optimization
4. **Alternative repartitioning:** More sophisticated shape decomposition may enable better predicate sharing

---

**End of Report**
