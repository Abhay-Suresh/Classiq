# Classiq Quantum Circuit Challenge 2026 - Final Report

**Date:** 2026-09-19  
**Challenge:** Quantum Phase Oracle for 64×64 Classiq Logo

---

## Final Verified Results

### Circuit Metrics
- **Depth:** 3,535
- **CX Count:** 2,337
- **Width:** 18 qubits (12 coordinates + 6 ancillas)
- **Basis Gates:** u3, cx only

### Verification Status
✅ **PASSED** - All correctness checks verified
- Max error: 4.97 × 10⁻¹⁶
- Ancilla error: 2.07 × 10⁻¹⁶
- Normalization error: 4.44 × 10⁻¹⁶
- All 1,097 black pixels correctly marked with -1 phase
- All 2,999 white pixels correctly left unchanged

---

## Optimization Journey

### Baseline (Starting Point)
- **Depth:** 5,329
- **CX Count:** 3,502
- **Strategy:** 18 independent rectangle checks

### Optimization Highlights
1. **X-Predicate Sharing + Control Reordering:** Depth 5,234 (-95)
2. **Y-Value Consolidation:** Depth 4,959 (-370)
3. **INTENSIVE Transpilation:** Depth 4,632 (-697)
4. **S-Complete Repartitioning:** Depth 4,361 (-968)
5. **D₂ Merged-Pairs Symmetry:** Depth 4,312 (-1,017)
6. **10-Control Hybrid:** Depth 3,992 (-1,337)
7. **S-First Control Ordering:** Depth 3,960 (-1,369)
8. **D₂ X-Consolidation:** Depth 3,820 (-1,509)
9. **D₂ Interleaved Edges:** Depth 3,792 (-1,537)
10. **pytket Post-Processing:** Depth 3,779 (-1,550)
11. **Reverse D₂ Ordering + pytket:** Depth 3,749 (-1,580, 29.65% reduction)
12. **Predicate Caching (nested control):** **Depth 3,535 (-214 / -182 CX, 33.68% total reduction)**, CX 2,337

---

## Final Oracle Structure

```python
@qperm
def logo_phase_oracle(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)

    # 1. Largest regions
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # 2. D1 outer shells with PREDICATE CACHING (nested control)
    # Cache (x >= 50) & (x <= 60) in an ancilla once, reuse for all D1 shells
    control((x >= 50) & (x <= 60)) {
        control((y >= 37) & (y <= 38), lambda: phase(pi))
        control((y >= 44) & (y <= 45), lambda: phase(pi))
    }
    control((x >= 51) & (x <= 59) & ((y == 36) | (y == 46)), lambda: phase(pi))
    control((x >= 53) & (x <= 57) & ((y == 35) | (y == 47)), lambda: phase(pi))

    # 3. D2 REVERSE edges [c4, c3, c2, c1]
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))
```

---

## Submission Checklist

✅ Circuit width ≤ 18 qubits  
✅ Basis gates: u3, cx only  
✅ Coordinates preserved (x, y unchanged)  
✅ Ancillas returned to |0⟩  
✅ Correct phase pattern  
✅ Global phase independent of coordinates  
✅ Depth: 3,535  
✅ CX count: 2,337  
