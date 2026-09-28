# Quantum Circuit Challenge 2026: Optimization Dashboard

## Current Champion: Multi-Variable Trie-Factored ESOP Oracle
- **Date**: 2026-09-28
- **Depth**: **1,703**
- **CX Count**: **1,638**
- **Width**: **18**
- **Max Error**: `2.05e-16` (Exact Match, < 1.0e-15 threshold)
- **Methodology**:
  - Found a 61-cube ESOP cover across 12 variables $x[0..5], y[0..5]$ via vectorized greedy XOR matching.
  - Constructed a recursive prefix decision trie over all 12 variables (using a `min_freq=2` split).
  - Common literal conditions are factored into nested `control()` blocks, completely eliminating redundant controls and reusing ancilla across the recursive hierarchy.
  - Synthesized with Classiq (DEPTH optimization, max_width=18), transpiled INTENSIVE, and finalized with PyTket `FullPeepholeOptimise` and `AutoRebase(u3, cx)`.

## Historical Progression
1. **Initial Baseline (Rectangular / PyTket FPO)**: Depth 3,198 / CX 2,082
2. **Tier 6 (Bar-First Permutation Search)**: Depth 2,928 / CX 1,945
3. **Rank-10 Separable Oracle**: Depth 2,750 / CX 2,771
4. **Factored ESOP (Y-Grouped Cover)**: Depth 2,263 / CX 2,299
5. **Multi-Variable Trie-Factored ESOP**: Depth **1,703** / CX **1,638** / Width 18

