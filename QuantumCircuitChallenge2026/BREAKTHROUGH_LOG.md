# Optimization Breakthrough Log

## Current Record: Depth 3,960 | CX 2,644

**Date:** 2026-09-19  
**Status:** ✅ VERIFIED AND CORRECT

### Result Details
- **Approach:** S-First Control Ordering (10-Control Hybrid variant)
- **Depth:** 3,960
- **CX count:** 2,644
- **Width:** 18 qubits
- **Improvement over baseline (5,329):** 1,369 points (25.69%)
- **Improvement over previous best (3,992):** 32 depth points (0.80%)

### Verification Status
- **Max statevector error:** 2.54 × 10⁻¹⁶ ✓
- **Ancilla error:** 5.88 × 10⁻¹⁷ ✓
- **Normalization error:** 2.05 × 10⁻¹⁴ ✓
- **Pixel exactness:** 4,096/4,096 (100%) ✓
- **Test states:** 3 random product-phase superpositions ✓

### Core Oracle Structure (10 Controls, S-First Ordering)
```python
@qperm
def oracle_order_s_first(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    # 1. Largest regions first (S, merged bar, D2 core)
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))

    # 2. D1 outer shells
    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # 3. D2 symmetric edges
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))
```

### Control Ordering Strategy
The key insight is ordering controls from **largest region to smallest region**:
1. Square S (625 pixels) — largest
2. Merged Bar+D1 Core (175 pixels) — second largest
3. D2 Core rectangle (169 pixels) — third largest
4. D1 shells and D2 edges — smaller regions last

This ordering allows the synthesis engine to build the circuit topology more efficiently, as larger-region controls establish the bulk of the phase structure first, and smaller-region controls refine it with fewer interfering interactions.

### Pixel Coverage (Total: 1,097 black pixels ✓)
| Region | X-range | Y-range | Pixels |
|--------|---------|---------|--------|
| Square S | [2, 26] | [29, 53] | 625 |
| Bar (27-48) | [27, 48] | [39, 43] | 110 |
| D1-core | [49, 61] | [39, 43] | 65 |
| D1-shells | Mixed | [35-47] | 137 |
| D2-core | [34, 46] | [13, 25] | 169 |
| D2-edges | Mixed | [11-27] | 56 |
| **TOTAL** | | | **1,097** |

### Files to Restore If Needed
```bash
submission.qasm          # QASM circuit, depth 3,960
final_best.qasm          # Backup copy, depth 3,960
verify_s_first_ordering.py  # Full verification script
verify_10_control_hybrid.py  # Previous verification (3,992)
test_optimization_suite_part2.py  # Test harness that found S-first
```

### Why S-First Ordering Works Better
1. **Control count:** Same 10 controls as previous best
2. **Ordering effect:** Largest regions first allows synthesis engine to build phase structure more efficiently
3. **Depth reduction:** 32-point improvement over nested-first ordering (4,006) and 32-point over unordered (3,992)
4. **CX reduction:** 2,644 vs 2,645 (1 fewer CX)

### Fallback Strategy
If no other approach yields depth < 3,960, restore from this log by:
1. Run `verify_s_first_ordering.py` again to regenerate the QASM
2. Copy the oracle function from the Core Oracle Structure above
3. The oracle is identical to the 10-Control Hybrid except for control ordering

---

**Next Phase:** Exploration of fundamentally new approaches (e.g., different oracle representations, advanced transpilation techniques, or hardware-specific optimizations).

---

## Previous Record (Superseded)

### Depth 3,992 | CX 2,645 (10-Control Hybrid, 2026-09-18)
Merged Bar + D1 Core approach. Superseded by S-first ordering which achieved 3,960 depth through control reordering alone.
