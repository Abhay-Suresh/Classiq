# Optimization Breakthrough Log

## Current Record: Depth 3,792 | CX 2,530

**Date:** 2026-09-19  
**Status:** ✅ VERIFIED AND CORRECT

### Result Details
- **Approach:** D2 Interleaved Edges (10-Control Hybrid)
- **Depth:** 3,792
- **CX count:** 2,530
- **Width:** 18 qubits
- **Improvement over baseline (5,329):** 1,537 points (28.84%)
- **Improvement over previous best (3,820):** 28 depth points (0.73%)

### Verification Status
- **Max statevector error:** 2.34 × 10⁻¹⁶ ✓
- **Ancilla error:** 5.80 × 10⁻¹⁷ ✓
- **Normalization error:** 1.90 × 10⁻¹⁴ ✓
- **Pixel exactness:** 4,096/4,096 (100%) ✓
- **Test states:** 3 random product-phase superpositions ✓

### Core Oracle Structure (D2 Interleaved Edges)
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

    # 3. D2 interleaved edges (optimized positioning)
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
```

### Key Breakthrough: D2 Interleaved Edges
Reordering the D2 edge controls (interleaving them with D1 shell controls) provided a 28-depth point improvement. This suggests that the Classiq synthesis engine benefits from balancing the "density" of phase controls applied to different coordinate regions.

### Pixel Coverage (Total: 1,097 black pixels ✓)
No change in pixel coverage — 1,097 black pixels correctly marked.

### Files to Restore If Needed
```bash
submission.qasm          # QASM circuit, depth 3,792
final_best.qasm          # Backup copy, depth 3,792
verify_3792.py           # Full verification script
```
