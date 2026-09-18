# Classiq Quantum Circuit Challenge 2026 - Final Report

**Date:** 2026-09-19  
**Challenge:** Quantum Phase Oracle for 64×64 Classiq Logo

---

## Final Verified Results

### Circuit Metrics
- **Depth:** 3,960
- **CX Count:** 2,644
- **Width:** 18 qubits (12 coordinates + 6 ancillas)
- **Basis Gates:** u3, cx only

### Verification Status
✅ **PASSED** - All correctness checks verified
- Max error: 2.54 × 10⁻¹⁶
- Ancilla error: 5.88 × 10⁻¹⁷
- Normalization error: 2.05 × 10⁻¹⁴
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

### Optimization 4: Square S Complete Repartitioning
- **Depth:** 4,361 (968 point improvement from baseline, **18.16%**)
- **CX Count:** 2,917
- **Strategy:** Keep Square S as one complete rectangle (y=29..53) instead of splitting top/bottom. Add merged bar extension (x=27..61, y=39..43) separately.

### Optimization 5: D₂ Merged-Pairs Symmetry
- **Depth:** 4,312 (1,017 point improvement from baseline)
- **CX Count:** 2,888
- **Strategy:** Core rectangle (x=34..46, y=13..25) plus symmetric edge columns using OR consolidation

### Optimization 6: 10-Control Hybrid (Merge Bar + D1 Core)
- **Depth:** 3,992 (1,337 point improvement from baseline)
- **CX Count:** 2,645
- **Strategy:** Merge Bar (x=27..48) and D1 core (x=49..61) into single control (x=27..61, y=39..43), reducing control count from 11 to 10

### Optimization 7: S-First Control Ordering ⭐ FINAL
- **Depth:** 3,960 (1,369 point improvement from baseline, **25.69%**)
- **CX Count:** 2,644
- **Strategy:** Reorder controls from largest region to smallest region. Put Square S (625px), merged Bar+D1 (175px), and D2 core (169px) first, followed by D1 shells and D2 edges.

---

## Key Technical Discoveries

### 1. Control Ordering is Critical
Reordering controls from largest region to smallest yielded a 32-depth improvement. The synthesis engine builds circuit topology more efficiently when larger-region controls establish the bulk phase structure first.

**S-first ordering:** S → merged bar → D2 core → D1 shells → D2 edges (Depth 3,960)  
**Nested-first ordering:** D2 edges → D1 shells → merged bar → S (Depth 4,006)  
**Unordered/default:** (Depth 3,992)

### 2. Transpilation Configuration Critical Path
The most important discovery was that `export()` must preserve the transpilation level:

```python
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

### 3. Predicate Sharing Strategy
Pre-computing shared X-conditions reduced redundant comparator synthesis.

### 4. Control Consolidation with Bitwise OR
Classical OR on quantum predicates enabled control reduction:
```python
control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
```

### 5. Merged Region Control
Combining Bar and D1 core into a single `(x >= 27) & (x <= 61)` control eliminated an entire control statement and enabled better synthesis.

---

## Unexplored Optimization Directions

The following strategies were tested but failed or regressed:

1. **Global Y-Symmetry (distance from y=41):** Requires 41 qubits — exceeds 18-qubit budget
2. **Distance-based Disks (Euclidean):** Requires 39 qubits — exceeds 18-qubit budget
3. **Width reduction (12-15):** Model requires at least 16 qubits
4. **Width 16-17:** Massive regression (8,846 and 4,558 depth respectively)
5. **Post-Synthesis Qiskit Opt:** Import error (`circuit_from_qasm` removed from qiskit.converters)
6. **Boolean Cube Decomposition:** No improvement (3,992, same as default)
7. **Direct U3/CX Basis:** No improvement (3,992, same as default)

---

## Files

### Submission Files
- `submission.qasm` - Verified transpiled circuit (depth 3,960)
- `final_best.qasm` - Backup copy of submission (depth 3,960)
- `verify_s_first_ordering.py` - Full verification script

### Documentation
- `classiq-challenge-baseline (1).ipynb` - Updated challenge notebook
- `FINAL_REPORT.md` - This document
- `BREAKTHROUGH_LOG.md` - Detailed breakthrough history
- `OPTIMIZATION_DASHBOARD.md` - Complete results dashboard

### Test Results
- `optimization_results_part1.json` - Part 1 optimization results (approaches 1-3)
- `optimization_results_part2.json` - Part 2 optimization results (approaches 4-11+)

---

## Submission Checklist

✅ Circuit width ≤ 18 qubits  
✅ Basis gates: u3, cx only  
✅ Coordinates preserved (x, y unchanged)  
✅ Ancillas returned to |0⟩  
✅ Correct phase pattern (-1 on black pixels, +1 on white pixels)  
✅ Global phase independent of coordinates  
✅ Depth: 3,960  
✅ CX count: 2,644  

---

## Competition Context

- **Baseline provided:** 5,329 depth
- **Our improvement:** 1,369 points (25.69% reduction)
- **Ranking metric:** Depth (primary), CX count (tiebreaker), submission time (second tiebreaker)

---

## Recommendations for Future Work

1. **Explore novel oracle representations:** Consider alternative formulations of the logo predicate that may admit deeper circuit optimizations
2. **Investigate Classiq synthesis internals:** Understanding why S-first ordering works could reveal deeper principles for control scheduling
3. **Try different transpilation levels:** TEST, MEDIUM, or custom configurations beyond INTENSIVE
4. **Hardware-specific optimization:** If targeting specific hardware topology, custom routing may help
5. **Multi-objective optimization:** Balance depth vs. CX count more carefully

---

**End of Report**
