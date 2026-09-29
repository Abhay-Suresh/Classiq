# Quantum Circuit Challenge 2026: Optimization Dashboard

## Current Champion: Iterative Trie-Factored 60-Cube Minimal ESOP Oracle
- **Date**: 2026-09-30
- **Depth**: **1,597**
- **CX Count**: **1,557**
- **Width**: **18**
- **Max Error**: `2.53e-16` (Exact Match, < 1.0e-15 threshold)
- **Ancilla Error**: `1.32e-16` (Zero Leakage)
- **Methodology**:
  - Synthesized a 60-cube minimal exact ESOP cover over 12 variables $x[0..5], y[0..5]$ (`optimized_esop_60.json`).
  - Constructed a multi-variable prefix decision trie using greedy score optimization (`score_mode='freq'`, `min_freq=2`).
  - Common literal prefix conditions are factored recursively into nested `control()` scopes in Classiq QMOD, completely avoiding redundant multi-controlled phase gates.
  - Synthesized with Classiq (DEPTH optimization, max_width=18 constraint), transpiled INTENSIVE to `['u3', 'cx']` basis, and iteratively pass-optimized using PyTket (`FullPeepholeOptimise`, `AutoRebase`, `RemoveRedundancies`, `SynthesiseTket`) until convergence (3 iterations).

## Historical Progression
1. **Initial Baseline (Rectangular / PyTket FPO)**: Depth 3,198 / CX 2,082
2. **Tier 6 (Bar-First Permutation Search)**: Depth 2,928 / CX 1,945
3. **Rank-10 Separable Oracle**: Depth 2,750 / CX 2,771
4. **Factored ESOP (Y-Grouped Cover)**: Depth 2,263 / CX 2,299
5. **Multi-Variable Trie-Factored ESOP**: Depth 1,703 / CX 1,638
6. **Deep Optimized Trie (len_weighted)**: Depth 1,698 / CX 1,617
7. **Max-Len Scored Trie + 15-Pass Deep PyTket**: Depth 1,664 / CX 1,595
8. **Classiq Trie-Factored 60-Cube Minimal ESOP**: Depth 1,604 / CX 1,557
9. **Iterative Convergence PyTket Pass**: Depth **1,597** / CX **1,557** / Width 18

