# Classiq Quantum Circuit Challenge 2026 - Final Report

**Date:** 2026-09-19  
**Challenge:** Quantum Phase Oracle for 64×64 Classiq Logo

---

## Final Verified Results

### Circuit Metrics
- **Depth:** 3,792
- **CX Count:** 2,530
- **Width:** 18 qubits (12 coordinates + 6 ancillas)
- **Basis Gates:** u3, cx only

### Verification Status
✅ **PASSED** - All correctness checks verified
- Max error: 2.34 × 10⁻¹⁶
- Ancilla error: 5.80 × 10⁻¹⁷
- Normalization error: 1.90 × 10⁻¹⁴
- Random test states: 3 superpositions
- All 1,097 black pixels correctly marked with -1 phase
- All 2,999 white pixels correctly left unchanged

---

## Optimization Journey

### Baseline (Starting Point)
- **Depth:** 5,329
- **CX Count:** 3,502
- **Strategy:** 18 independent rectangle checks

### Optimization 1: X-Predicate Sharing + Control Reordering
- **Depth:** 5,234 (-95 from baseline)
- **CX Count:** 3,492
- **Strategy:** Pre-compute 9 shared X-interval predicates

### Optimization 2: Y-Value Consolidation
- **Depth:** 4,959 (-370 from baseline)
- **CX Count:** 3,312
- **Strategy:** Combine symmetric rows using bitwise OR: `(y == 12) | (y == 26)`

### Optimization 3: INTENSIVE Transpilation
- **Depth:** 4,632 (-697 from baseline, 13.08%)
- **CX Count:** 3,126
- **Strategy:** Use `TranspilationOption.INTENSIVE` instead of `AUTO_OPTIMIZE`

### Optimization 4: S-Complete Repartitioning
- **Depth:** 4,361 (-968 from baseline, 18.16%)
- **CX Count:** 2,917
- **Strategy:** Keep Square S as one complete rectangle (y=29..53)

### Optimization 5: D₂ Merged-Pairs Symmetry
- **Depth:** 4,312 (-1,017 from baseline)
- **CX Count:** 2,888
- **Strategy:** Core rectangle plus symmetric edge columns

### Optimization 6: 10-Control Hybrid (Merge Bar + D1 Core)
- **Depth:** 3,992 (-1,337 from baseline)
- **CX Count:** 2,645
- **Strategy:** Merge Bar and D1 core into single control at x=27..61, y=39..43

### Optimization 7: S-First Control Ordering
- **Depth:** 3,960 (-1,369 from baseline, 25.69%)
- **CX Count:** 2,644
- **Strategy:** Reorder controls from largest region to smallest

### Optimization 8: D₂ X-Consolidation
- **Depth:** 3,820 (-1,509 from baseline, 28.32%)
- **CX Count:** 2,518
- **Strategy:** Consolidate symmetric D2 edges: `((x == 33) | (x == 47))` and `((x == 32) | (x == 48))`

### Optimization 9: D₂ Interleaved Edges ⭐ FINAL
- **Depth:** 3,792 (-1,537 from baseline, **28.84%**)
- **CX Count:** 2,530
- **Strategy:** Interleave D2 edge controls to balance phase control density

---

## Final Oracle Structure

```python
@qperm
def oracle_d2_edges_middle(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    # 1. Largest regions
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # 2. D1 outer shells
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # 3. D2 interleaved edges
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
```

---

## Key Technical Discoveries

### 1. Control Consolidation with Bitwise OR
The most powerful optimization came from consolidating symmetric controls using bitwise OR on equality checks:
- Y-symmetry: `(y == 36) | (y == 46)` instead of two separate controls
- X-symmetry: `(x == 33) | (x == 47)` instead of two separate controls

### 2. Control Ordering Matters
Ordering controls from largest to smallest region improved depth by 32 points (3,992 → 3,960).

### 3. Control Interleaving
Interleaving D2 edge controls among D1 shells balanced phase control density, yielding an additional 28-point improvement (3,820 → 3,792).

### 4. INTENSIVE Transpilation Critical
Setting `transpilation_level=TranspilationOption.INTENSIVE` in both transpilation AND export was essential — saved 327 depth points over AUTO_OPTIMIZE.

### 5. Region Merging
Merging Bar (x=27..48) and D1 core (x=49..61) into one control eliminated redundancy and saved 320 depth points.

---

## Files

### Submission Files
- `submission.qasm` - Verified transpiled circuit (depth 3,792)
- `final_best.qasm` - Backup copy (depth 3,792)
- `submission.qmod` - Qmod source

### Documentation
- `FINAL_REPORT.md` - This document
- `BREAKTHROUGH_LOG.md` - Detailed breakthrough history
- `OPTIMIZATION_DASHBOARD.md` - Complete results
- `classiq-challenge-baseline (1).ipynb` - Main notebook

---

## Submission Checklist

✅ Circuit width ≤ 18 qubits  
✅ Basis gates: u3, cx only  
✅ Coordinates preserved (x, y unchanged)  
✅ Ancillas returned to |0⟩  
✅ Correct phase pattern  
✅ Global phase independent of coordinates  
✅ Depth: 3,792  
✅ CX count: 2,530  

---

## Competition Context

- **Baseline provided:** 5,329 depth
- **Our improvement:** 1,537 points (28.84% reduction)
- **Ranking metric:** Depth (primary), CX count (tiebreaker)

---

**End of Report**
