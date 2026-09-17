# Classiq Quantum Circuit Challenge 2026 - Optimization Report

## Final Results

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| **Depth** | 5,329 | **5,250** | **-79 (-1.5%)** |
| **CX Count** | 3,502 | **3,492** | **-10 (-0.3%)** |
| **Width** | 18 | 18 | Maintained |
| **Correctness** | ✓ | ✓ | All 1,097 pixels |

---

## Optimization Approach: X-Predicate Sharing

### Problem
The baseline implementation evaluates 18 separate rectangle conditions independently. Many rectangles share the same X-coordinate bounds but apply to different Y-ranges.

### Key Insight
By pre-computing shared X-conditions and reusing them across multiple Y-ranges, we reduce redundant comparisons and lower circuit depth.

### Implementation
**9 Shared X-Conditions:**
```qmod
is_S_x = (x >= 2) & (x <= 26)          # Square S
is_d2_x_38_42 = (x >= 38) & (x <= 42)  # D2 circle (reused 2×)
is_d2_x_36_44 = (x >= 36) & (x <= 44)  # D2 circle (reused 2×)
is_d2_x_34_46 = (x >= 34) & (x <= 46)  # D2 circle (reused 2×)
is_d2_x_33_47 = (x >= 33) & (x <= 47)  # D2 circle (reused 2×)
is_d2_x_32_48 = (x >= 32) & (x <= 48)  # D2 circle (reused 1×)
is_d1_x_53_57 = (x >= 53) & (x <= 57)  # D1 circle (reused 2×)
is_d1_x_51_59 = (x >= 51) & (x <= 59)  # D1 circle (reused 2×)
is_d1_x_50_60 = (x >= 50) & (x <= 60)  # D1 circle (reused 2×)
```

**16 Control Statements:**
1. Merged rectangle: `x ∈ [2,61], y ∈ [39,43]` (300 pixels)
2. Square S bottom: `is_S_x & y ∈ [29,38]` (250 pixels)
3. Square S top: `is_S_x & y ∈ [44,53]` (250 pixels)
4-12. D2 circle: 9 conditions with shared X-predicates (225 pixels)
13-16. D1 circle: 4 conditions with shared X-predicates (72 pixels)

**Total: 16 controls** (vs 18 in baseline)

---

## What We Explored

### ✓ X-Predicate Sharing (IMPLEMENTED)
- **Result:** 79 depth reduction (1.5%)
- **Why it works:** Classiq synthesis recognizes reused X-conditions and optimizes them

### ✗ Y-Predicate Sharing (REJECTED)
- **Result:** 1,878 depth reduction (35%) but **INCORRECT**
- **Problem:** Y-ranges in D2 have overlapping X-intervals that caused double-coverage
- **Example:** Pixel (38,11) matched 5 different D2 conditions → phase flipped 5 times → wrong!
- **Lesson:** Must use disjoint rectangles to avoid double phase-flips

### ✗ Mathematical Circle Formulas
- **Idea:** Use `(x-55)² + (y-41)² ≤ 42` directly
- **Problem:** Arithmetic operations require 67+ qubits
- **Result:** Exceeded 18-qubit maximum

### ✗ Single Giant Boolean OR
- **Idea:** Combine all 18 rectangles into one condition
- **Problem:** Requires 37 qubits for boolean workspace
- **Result:** Exceeded 18-qubit maximum

### ✗ Bitwise Operations
- **Idea:** Use `(y & 48) == 32` to check bit patterns
- **Problem:** Combined bitwise ops + comparisons require 30 qubits
- **Result:** Exceeded 18-qubit maximum

### ✗ ESOP/BDD Minimization
- **Idea:** Use classical logic synthesis on 1,097 minterms
- **Problem:** Sympy couldn't handle 12 variables efficiently; need external tools (ABC, Espresso)
- **Result:** Not feasible in current environment

---

## Analysis

### Rectangle Structure
The logo's 18 disjoint rectangles break down as:
- **D2 circle** (y=11-27): 9 rectangles with nested X-ranges
- **Square S** (y=29-53): Split into 3 parts by the merged rectangle
- **Bar B** (y=39-43): Merged with S and D1 into one large rectangle
- **D1 circle** (y=35-47): 6 rectangles

### X-Pattern Reuse
| X-Interval | Used in | Reuse Count |
|------------|---------|-------------|
| [38, 42]   | y=11, y=27 | 2× |
| [36, 44]   | y=12, y=26 | 2× |
| [34, 46]   | y∈[13,14], y∈[24,25] | 2× |
| [33, 47]   | y∈[15,16], y∈[22,23] | 2× |
| [2, 26]    | y∈[29,38], y∈[44,53] | 2× |
| [53, 57]   | y=35, y=47 | 2× |
| [51, 59]   | y=36, y=46 | 2× |
| [50, 60]   | y∈[37,38], y∈[44,45] | 2× |

**Result:** 8 out of 9 shared conditions are reused 2×, saving ~8-10 gates per reuse.

---

## Why Further Optimization is Difficult

1. **Qubit Budget Constraint:** The 18-qubit maximum prevents combining multiple boolean operations
2. **Disjoint Rectangle Requirement:** To avoid double phase-flips, rectangles must be non-overlapping
3. **Synthesis Efficiency:** Classiq's synthesis is already quite optimized for simple comparisons
4. **Missing External Tools:** Full ESOP/BDD minimization requires specialized tools not available

---

## Potential Future Improvements

If pursuing further optimization with proper tools:

1. **ESOP/BDD with ABC** (Est. 500-1,500 depth reduction)
   - Install Berkeley ABC or Espresso
   - Convert 1,097-minterm truth table to minimal logic
   - Translate back to Qmod

2. **Hybrid X+Y Sharing with Disjoint Partitions**
   - Carefully partition rectangles to avoid overlaps
   - Share both X and Y conditions where safe

3. **Bit-Level Karnaugh Maps** (Est. 800-2,000 depth reduction)
   - Analyze 12-bit patterns across all 1,097 pixels
   - Use classical logic minimization tools
   - Requires significant manual translation effort

---

## Verification

The optimized solution:
- ✓ Covers all 1,097 black pixels exactly once
- ✓ Maintains all 12 coordinate qubits unchanged
- ✓ Returns all ancillas to |0⟩ state
- ✓ Uses only u3 and cx basis gates
- ✓ Stays within 18-qubit maximum width

---

## Files Generated

- `submission.qmod` - Optimized Qmod source with X-predicate sharing
- `submission.qasm` - Transpiled OpenQASM 2.0 circuit (depth 5,250)
- `submission.synthesis_options.json` - Synthesis configuration
- `OPTIMIZATION_REPORT.md` - This report

---

## Conclusion

We achieved a **1.5% depth improvement (79 points)** through systematic X-predicate sharing and reuse. While exploring Y-predicate sharing showed promising results (35% improvement), it produced incorrect output due to overlapping conditions causing double phase-flips.

The current solution represents the practical optimum given:
- Qmod's 18-qubit constraint
- The requirement for disjoint rectangles
- Available tools and synthesis capabilities

**The solution is correct, verified, and ready for submission.**

---

**Optimized by:** X-Predicate Sharing Strategy  
**Date:** September 18, 2026  
**Depth:** 5,250 | **CX Count:** 3,492 | **Width:** 18 qubits
