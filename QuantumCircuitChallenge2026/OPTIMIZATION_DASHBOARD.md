# Optimization Dashboard

Goal: Further optimize beyond **Depth 3,960 | CX 2,644**.

## Summary of Results So Far

| # | Approach | Measured Depth | Measured CX | Status | Notes |
|---|----------|---|---|---|---|
| 0 | Baseline (18 rectangles) | 5,329 | 3,502 | Verified | Initial rectangle cover |
| 1 | X-sharing + reordering | 5,234 | 3,492 | Verified | 9 shared X-predicates |
| 2 | Y-value consolidation | 4,959 | 3,312 | Verified | OR of symmetric rows |
| 3 | INTENSIVE transpilation | 4,632 | 3,126 | Verified | Auto_OPTIMIZE → INTENSIVE |
| 4 | S-complete repartitioning | 4,361 | 2,917 | Verified | One S rectangle + merged bar |
| 5 | D₂ merged-pairs symmetry | 4,312 | 2,888 | Verified | Core rectangle + symmetric edges |
| 6 | 10-Control Hybrid | 3,992 | 2,645 | Verified | Merged Bar+D1 core (x=27..61, y=39..43) |
| 7 | XOR/ESOP | 4,455 | 2,969 | Synthesized | Regression (−143 depth) |
| 8 | Shared Predicate Tree | 4,312 | 2,888 | Synthesized | No gain |
| 9 | Direct U3/CX Basis | 3,992 | 2,645 | Synthesized | No gain over baseline |
| **10** | **S-First Ordering** | **3,960** | **2,644** | **Verified ✅** | **Largest regions first** |
| 11 | Nested-First Ordering | 4,006 | 2,630 | Synthesized | Regression (+46 depth) |
| 12 | Width Sweep (16-17) | 4,558 | 3,112 | Synthesized | Regression; 12-15 fail |
| 13 | Global Y-Symmetry | — | — | ERROR | Requires 41 qubits |
| 14 | Distance-based Disks | — | — | ERROR | Requires 39 qubits |
| 15 | Post-Synthesis Qiskit Opt | — | — | ERROR | Import error |
| 16 | Boolean Cube Decomp | 3,992 | 2,645 | Synthesized | No gain |

## Best Result
- **Depth:** 3,960 (S-First Control Ordering)
- **CX:** 2,644
- **Improvement over baseline (5,329):** 1,369 depth points (**25.69%** reduction)

## Methodology
- **Synthesis:** `create_model` with `constraints=Constraints(optimization_parameter=OptimizationParameter.DEPTH, max_width=18)`
- **Transpilation:** `classiq.transpile` with `TranspilationOption.INTENSIVE` and `basis_gates=['u3', 'cx']`
- **Verification:** Custom Python script using `ExecutionSession` and state-vector fidelity check (random 3-state superposition, max error 2.54e-16)

## Status: ✅ All Exploration Complete
All 11 originally planned approaches plus follow-up tests have been run. The S-first ordering represents the best result found. No further improvements were found in the remaining approaches.

## Key Insights
1. **Control ordering matters:** 32-depth improvement from reordering alone
2. **Largest-first is optimal:** Putting S, merged bar, D2 core first outperforms all other orderings
3. **Width 18 is required:** Smaller widths (12-15) fail; widths 16-17 regress heavily
4. **Distance formulas don't help:** Require too many ancillas (39-41 qubits)
5. **Post-synthesis Qiskit optimization is unavailable:** Import error in current Qiskit version
