# Quantum Circuit Challenge 2026: Optimization Dashboard

## Current Champion: Max-Len Scored Trie-Factored ESOP Oracle (15-Pass Deep PyTket)
- **Date**: 2026-09-29
- **Depth**: **1,664**
- **CX Count**: **1,595**
- **Width**: **18**
- **Max Error**: `2.06e-16` (Exact Match, < 1.0e-15 threshold)
- **Ancilla Error**: `1.59e-16` (Zero Leakage)
- **Methodology**:
  - Found a 61-cube ESOP cover across 12 variables $x[0..5], y[0..5]$ via vectorized greedy XOR matching.
  - Constructed a recursive prefix decision trie using `max_len` scoring (`score = max_cube_length × frequency`, `min_freq=2`).
  - Common literal conditions are factored into nested `control()` blocks, completely eliminating redundant controls and reusing ancilla across the recursive hierarchy.
  - Synthesized with Classiq (DEPTH optimization, max_width=18), transpiled INTENSIVE, and finalized with 15 iterations of PyTket deep optimization (`FullPeepholeOptimise`, `SynthesiseTket`, `OptimisePhaseGadgets`, `AutoRebase(u3, cx)`, `RemoveRedundancies`).

## Historical Progression
1. **Initial Baseline (Rectangular / PyTket FPO)**: Depth 3,198 / CX 2,082
2. **Tier 6 (Bar-First Permutation Search)**: Depth 2,928 / CX 1,945
3. **Rank-10 Separable Oracle**: Depth 2,750 / CX 2,771
4. **Factored ESOP (Y-Grouped Cover)**: Depth 2,263 / CX 2,299
5. **Multi-Variable Trie-Factored ESOP**: Depth 1,703 / CX 1,638
6. **Deep Optimized Trie (len_weighted)**: Depth 1,698 / CX 1,617
7. **Max-Len Scored Trie + 15-Pass Deep PyTket**: Depth **1,664** / CX **1,595** / Width 18

