# Optimization Breakthrough Log

## Current Record: Depth 3,749 | CX 2,519

**Date:** 2026-09-19  
**Status:** ✅ VERIFIED AND CORRECT

### Result Details
- **Approach:** Reverse D2 Ordering + pytket Post-Processing
- **Depth:** 3,749
- **CX count:** 2,519
- **Width:** 18 qubits
- **Improvement over baseline (5,329):** 1,580 points (29.65%)
- **Verification:** max error 4.97e-16, all 4,096 states correct

### Verification Status
- **Max statevector error:** 4.97 × 10⁻¹⁶ ✓
- **Ancilla error:** 2.07 × 10⁻¹⁶ ✓
- **Normalization error:** 4.44 × 10⁻¹⁶ ✓
- **Pixel exactness:** 4,096/4,096 (100%) ✓
- **Test states:** Full statevector verification ✓

### Core Oracle Structure (Reverse D2 Interleaved Edges)
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

    # 3. D2 REVERSE edges [c4, c3, c2, c1] - OPTIMIZED
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))
```

### Key Breakthrough: Reverse D2 Ordering
Reversing the order of D2 edge controls from [c1, c2, c3, c4] to [c4, c3, c2, c1] combined with pytket's FullPeepholeOptimise provided a final 30-depth point improvement.

### Files
- `submission.qasm` - Verified transpiled circuit (depth 3,749)
- `submission.qmod` - QMOD source
- `verify_submission.py` - Full verification script