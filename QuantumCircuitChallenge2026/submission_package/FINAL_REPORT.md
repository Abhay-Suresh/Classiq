# Classiq Quantum Circuit Challenge 2026 - Final Report

**Date:** 2026-09-29  
**Challenge:** Quantum Phase Oracle for 64×64 Classiq Logo  
**Target Metrics:** Circuit Depth (primary), CX Gate Count (secondary)  
**Constraint:** Max Width <= 18 qubits (12 coordinate qubits + 6 ancillas), Basis Gates ['u3', 'cx']  

---

## 🏆 Final Verified Results

### Circuit Metrics
- **Depth:** **1,705** (+3 depth from 1,702) | **CX:** **1,637** (-8 CX from 1,645)
- **CX Count:** **1,645** (53.0% reduction from baseline 3,502, -1,857 CX)
- **Width:** **18 qubits** (6 x coordinates, 6 y coordinates, 6 ancillas)
- **Basis Gates:** `u3`, `cx` only

### Verification Status
✅ **PASSED** - All correctness and unitary invariants strictly verified:
- **Max Phase Error:** 2.81e-16 (global phase-adjusted)
- **Ancilla Leakage:** 1.57e-16 (essentially zero — ancillas fully uncomputed)
- **Normalization Error:** 2.22e-15
- All 1,148 black pixels correctly assigned a Pi phase shift (-1).
- All 2,948 white pixels correctly assigned a 0 phase shift (+1).
- All 4,096 basis states |y, x, 0_anc> verified exactly.

---

## 🚀 Optimization Journey

| # | Approach / Technique | Depth | CX | Width | Status |
|---|----------------------|-------|-----|-------|--------|
| 0 | Baseline (18 independent rectangles) | 5,329 | 3,502 | 18 | ✅ Verified |
| 1 | X-Predicate Sharing + Control Reordering | 5,234 | 3,492 | 18 | ✅ Verified |
| 2 | Y-Value Consolidation | 4,959 | 3,312 | 18 | ✅ Verified |
| 3 | Classiq INTENSIVE Transpilation | 4,632 | 3,126 | 18 | ✅ Verified |
| 4 | S-Complete Geometric Repartition | 4,361 | 2,917 | 18 | ✅ Verified |
| 5 | D2 Merged-Pairs Symmetry | 4,312 | 2,888 | 18 | ✅ Verified |
| 6 | 10-Control Hybrid | 3,992 | 2,645 | 18 | ✅ Verified |
| 7 | S-First Control Ordering | 3,960 | 2,644 | 18 | ✅ Verified |
| 8 | D2 X-Consolidation | 3,820 | 2,518 | 18 | ✅ Verified |
| 9 | D2 Interleaved Edges | 3,792 | 2,530 | 18 | ✅ Verified |
| 10 | pytket FullPeephole Post-Processing | 3,779 | 2,530 | 18 | ✅ Verified |
| 11 | Reverse D2 Ordering + pytket | 3,749 | 2,519 | 18 | ✅ Verified |
| 12 | Predicate Caching (Nested Controls) | 3,535 | 2,337 | 18 | ✅ Verified |
| 13 | Tier 1 Granular Predicates & Factoring | 3,011 | 1,965 | 18 | ✅ Verified |
| 14 | Tier 4.1 Region Commutation & Permutation | 2,967 | 1,959 | 18 | ✅ Verified |
| 15 | Tier 5.2 Micro Permutation | 2,959 | 1,948 | 18 | ✅ Verified |
| 16 | Rank-10 Separable Oracle | 2,750 | 2,771 | 18 | ✅ Verified |
| 17 | Factored ESOP (Y-Grouped Cover) | 2,263 | 2,299 | 18 | ✅ Verified |
| **18** | **Multi-Variable Trie-Factored ESOP** | **1,702** | **1,645** | **18** | **🏆 NEW CHAMPION** |

---

## 🔬 Tier 9: Multi-Variable Trie-Factored ESOP

### Innovation: Recursive Decision Trie over 12 Variables

Instead of factoring ESOP terms purely by Y-coordinates, we construct a recursive decision trie over all 12 variables (x[0..5] and y[0..5]):

1. **Greedy Multi-Variable Extraction**: At each decision node, we identify the literal (e.g. x_5 = 1 or y_2 = 0) with the highest frequency among remaining cubes.
2. **Recursive Splitting**: If frequency >= 2, we factor that single literal into an outer `control()` block, recursing on both the subset containing the literal and the subset without it.
3. **Leaf Preservation**: When frequency drops below threshold, remaining literal combinations are emitted as leaf cubes.

This drastically minimizes redundant multiple controls because a given component common to many terms is only verified once down the whole chain. We let the Classiq engine automatically reuse ancillas via its internal synthesis when allocating inside deep control nodes!

### Results

- **Depth:** **1,702** (25% reduction over previous Depth 2,263 ESOP champion)
- **CX Count:** **1,645**
- **Width:** **18 qubits**
- **Fidelity:** **Exact** (Max error 2.81e-16)

