# Optimization Dashboard

**Current Best:** Depth 3,792 | CX 2,530

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
| **9** | **D₂ Interleaved Edges** | **3,792** | **2,530** | **+28** | **✅ FINAL** |

**Total improvement:** 1,537 depth points (28.84% reduction from baseline)

## Key Insights

1. **Control consolidation:** Combining symmetric controls with bitwise OR (`(x==33)|(x==47)`) was the single most effective technique (+140 depth in one step)

2. **Control ordering:** Largest regions first improves synthesis (+32 depth)

3. **Control interleaving:** Balancing phase control density across regions (+28 depth)

4. **INTENSIVE transpilation:** Essential for all optimizations (+327 depth improvement alone)

5. **Region merging:** Merging Bar+D1 core eliminated redundancy (+320 depth)

## Approaches Tested (No Improvement)

- XOR/ESOP decomposition: Regressed to 4,455 depth
- Shared predicate tree: No gain (4,312)
- Direct U3/CX basis: No gain (3,992)
- Nested-first ordering: Regressed to 4,006 depth
- Boolean cube decomp: No gain (3,992)
- Width sweep (16-17): Massive regression
- Global Y-symmetry: Requires 41 qubits (failed)
- Distance-based disks: Requires 39 qubits (failed)
- D1 shell consolidation: Requires 19 qubits or invalid predicates (failed)
- Post-synthesis Qiskit: Import error (failed)

## Methodology

- **Synthesis:** `OptimizationParameter.DEPTH`, `max_width=18`
- **Transpilation:** `TranspilationOption.INTENSIVE`, `basis_gates=['u3', 'cx']`
- **Verification:** 3 random product-phase superpositions, max error < 1e-10
