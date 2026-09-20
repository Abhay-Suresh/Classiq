# Optimization Dashboard

**Current Best:** Depth 3,535 | CX 2,337

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
| 11 | Reverse D₂ Ordering + pytket | 3,749 | 2,519 | +30 | ✅ Verified |
| **12** | **Predicate Caching (Nested Controls)** | **3,535** | **2,337** | **+214** | **✅ FINAL BEST** |

**Total improvement:** 1,794 depth points (33.68% reduction from baseline)

## Key Insights

1. **Predicate Caching via Nested Controls:** Caching heavy 6-bit arithmetic comparator `(x >= 50) & (x <= 60)` into an ancilla scratchpad once and reusing it across multiple conditional phase gates eliminated redundant carry chains (+214 depth, +182 CX).
2. **Control Consolidation:** Combining symmetric controls with bitwise OR (`(x==33)|(x==47)`) eliminates redundant comparator trees (+140 depth).
3. **INTENSIVE Transpilation:** Essential for all optimizations (+327 depth improvement alone).
4. **Region Merging:** Merging Bar+D1 core eliminated duplicate coverage (+320 depth).
5. **Reverse D₂ Ordering + pytket:** Optimizes gate density, commutations, and peephole rotation merging (+43 depth total).
6. **Sequential Ancilla Reuse vs Concurrent Locking:** Exploiting all 6 available ancillas sequentially maximizes parallel synthesis width without exceeding the 18-qubit hardware budget.
