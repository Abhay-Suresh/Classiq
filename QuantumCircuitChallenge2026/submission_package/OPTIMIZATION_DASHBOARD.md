# Optimization Dashboard

**Current Best:** Depth 2,959 | CX 1,948

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
| 12 | Predicate Caching (Nested Controls) | 3,535 | 2,337 | +214 | ✅ Verified |
| 13 | Tier 1 Granular Predicates | 3,011 | 1,965 | +524 | ✅ Verified |
| 14 | Tier 4.1 Region Permutation | 2,967 | 1,959 | +44 | ✅ Verified |
| **15** | **Tier 5.2 Micro Permutation (D2 Core->X->Y, D1 Shells->Bar)** | **2,959** | **1,948** | **+8** | **✅ FINAL BEST** |

**Total improvement:** 2,370 depth points (44.47% reduction from baseline)

## Key Insights

1. **Predicate Caching via Nested Controls:** Caching heavy 6-bit arithmetic comparator `(x >= 50) & (x <= 60)` into an ancilla scratchpad once and reusing it across multiple conditional phase gates eliminated redundant carry chains.
2. **Control Consolidation:** Combining symmetric controls with bitwise OR (`(x==33)|(x==47)`) eliminates redundant comparator trees.
3. **Region Evaluation Commutation & Gate Cancellation:** Because all phase operations commute mathematically, altering evaluation order of independent spatial regions cancels redundant CX pairs across adjacent multi-controlled gates. Placing D2 regions contiguously before D1 regions allows pytket to maximally commute and cancel rotations (broke the 3,000 threshold to 2,967).
4. **Sequential Ancilla Reuse vs Explicit Uncomputation:** Explicitly attempting to save depth via `anc ^= ...` fails dramatically (verified depth 6,317–7,746). Instead, nesting regions within classiq `control()` closures correctly maximizes compiler-managed uncomputation without blowing up depth.
