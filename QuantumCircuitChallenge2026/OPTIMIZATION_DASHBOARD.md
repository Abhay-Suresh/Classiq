# Optimization Dashboard

**Current Best:** Depth 3,749 | CX 2,519

## Complete Optimization History

| # | Approach | Depth | CX | Improvement | Status |
|---|----------|-------|-----|-------------|--------|
| 0 | Baseline (18 rectangles) | 5,329 | 3,502 | — | ✅ Verified |
| 1 | X-sharing + reordering | 5,234 | 3,492 | +95 | ✅ Verified |
| 2 | Y-value consolidation | 4,959 | 3,312 | +275 | ✅ Verified |
| 3 | INTENSIVE transpilation | 4,632 | 3,126 | +327 | ✅ Verified |
| 4 | S-complete repartition | 4,361 | 2,917 | +271 | ✅ Verified |
| 5 | D₂ merged-pairs | 4,312 | 2,888 | +49 | ✅ Verified |
| 6 | 10-Control Hybrid | 3,992 | 2,645 | +320 | ✅ Verified |
| 7 | S-First Ordering | 3,960 | 2,644 | +32 | ✅ Verified |
| 8 | D₂ X-Consolidation | 3,820 | 2,518 | +140 | ✅ Verified |
| 9 | D₂ Interleaved Edges | 3,792 | 2,530 | +28 | ✅ Verified |
| 10 | pytket Post-Processing | 3,779 | 2,530 | +13 | ✅ Verified |
| **11** | **Reverse D₂ Ordering + pytket** | **3,749** | **2,519** | **+30** | **✅ FINAL** |

**Total improvement:** 1,580 depth points (29.65% reduction from baseline)

## Key Insights

1. **Control consolidation:** Combining symmetric controls with bitwise OR (`(x==33)|(x==47)`) was the single most effective technique (+140 depth in one step)
2. **Control ordering:** Largest regions first improves synthesis (+32 depth)
3. **Control interleaving:** Balancing phase control density across regions (+28 depth)
4. **INTENSIVE transpilation:** Essential for all optimizations (+327 depth improvement alone)
5. **Region merging:** Merging Bar+D1 core eliminated redundancy (+320 depth)
6. **Reverse D2 ordering + pytket:** Optimizes gate density and schedule (+43 depth total)
