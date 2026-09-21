# Classiq Quantum Circuit Challenge 2026 - Final Report

**Date:** 2026-09-21  
**Challenge:** Quantum Phase Oracle for 64×64 Classiq Logo  
**Target Metrics:** Circuit Depth (primary), CX Gate Count (secondary)  
**Constraint:** Max Width ≤ 18 qubits (12 coordinate qubits + 6 ancillas), Basis Gates `['u3', 'cx']`  

---

## 🏆 Final Verified Results

### Circuit Metrics
- **Depth:** **2,959** (44.47% reduction from baseline)
- **CX Count:** **1,948** (44.37% reduction from baseline)
- **Total Gates:** **3,864**
- **Width:** **18 qubits** (6 $x$ coordinates, 6 $y$ coordinates, 6 ancillas)
- **Basis Gates:** `u3`, `cx` only

### Verification Status
✅ **PASSED** - All correctness and unitary invariants strictly verified:
- **Max Phase Error:** $3.62 \times 10^{-16}$
- **Ancilla Residual Error:** $2.26 \times 10^{-16}$
- **Normalization Error:** $4.44 \times 10^{-16}$
- All 1,097 black pixels correctly assigned a $\pi$ phase shift ($-1$).
- All 2,999 white pixels correctly assigned a $0$ phase shift ($+1$).

---

## 🚀 Optimization Journey

| # | Approach / Technique | Depth | CX | Depth Δ | Status |
|---|----------------------|-------|-----|---------|--------|
| 0 | Baseline (18 independent rectangles) | 5,329 | 3,502 | — | ✅ Verified |
| 1 | X-Predicate Sharing + Control Reordering | 5,234 | 3,492 | -95 | ✅ Verified |
| 2 | Y-Value Consolidation | 4,959 | 3,312 | -275 | ✅ Verified |
| 3 | Classiq INTENSIVE Transpilation | 4,632 | 3,126 | -327 | ✅ Verified |
| 4 | S-Complete Geometric Repartition | 4,361 | 2,917 | -271 | ✅ Verified |
| 5 | D₂ Merged-Pairs Symmetry | 4,312 | 2,888 | -49 | ✅ Verified |
| 6 | 10-Control Hybrid | 3,992 | 2,645 | -320 | ✅ Verified |
| 7 | S-First Control Ordering | 3,960 | 2,644 | -32 | ✅ Verified |
| 8 | D₂ X-Consolidation | 3,820 | 2,518 | -140 | ✅ Verified |
| 9 | D₂ Interleaved Edges | 3,792 | 2,530 | -28 | ✅ Verified |
| 10 | pytket FullPeephole Post-Processing | 3,779 | 2,530 | -13 | ✅ Verified |
| 11 | Reverse D₂ Ordering + pytket | 3,749 | 2,519 | -30 | ✅ Verified |
| 12 | Predicate Caching (Nested Controls) | 3,535 | 2,337 | -214 | ✅ Verified |
| 13 | Tier 1 Granular Predicates & Factoring | 3,011 | 1,965 | -524 | ✅ Verified |
| 14 | Tier 4.1 Region Commutation & Permutation | 2,967 | 1,959 | -44 | ✅ Verified |
| **15** | **Tier 5.2 Micro Permutation (D2 Core→X→Y, D1 Shells→Bar)** | **2,959** | **1,948** | **-8** | **🏆 CHAMPION** |

---

## 🔬 Key Innovations & Optimization Strategies

1. **Predicate Caching via Nested Closures:**
   By nesting disjoint sub-checks inside continuous multi-bit interval closures (`control(x_range, lambda: (control(y1, ...), control(y2, ...)))`), Classiq's synthesis engine computes the 6-bit arithmetic comparator carry chain into an ancilla *once* and reuses it across sequential phase gates, eliminating redundant evaluations.

2. **Phase Oracle Commutation Exploitation:**
   Since all conditional diagonal phase gates commute $[U_{\phi_1}, U_{\phi_2}] = 0$, the spatial evaluation order is completely unconstrained. By ordering D₂ components contiguously before D₁, and sequencing within blocks from outer shells into the inner bar, adjacent Multi-Controlled X (MCX) ladders allow PyTket's `FullPeepholeOptimise` pass to maximally cancel intermediate $CX$ pairs across gate boundaries.

3. **Compiler-Managed Ancilla Lifecycle:**
   Manual uncomputation schemes (`anc ^= predicate`) fail due to rigid sequential ancilla dependency graphs, bloating depth to >6,000. Expressing predicates cleanly via functional Python closures allowed Classiq's synthesis synthesis engine to dynamically schedule borrowable ancillas within the 18-qubit hardware budget.

4. **Multi-Stage Optimization Pipeline:**
   - **Synthesis:** Classiq synthesis with depth optimization target (`max_width=18`).
   - **Transpilation:** Classiq `INTENSIVE` level transpilation targeting `['u3', 'cx']`.
   - **Peephole & Phase-Gadget Simplification:** PyTket `FullPeepholeOptimise` and `OptimisePhaseGadgets` pass sequences.
