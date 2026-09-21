# Classiq Quantum Circuit Challenge 2026

![Classiq Logo Phase Oracle](https://img.shields.io/badge/Depth-2%2C959-brightgreen)
![CX Count](https://img.shields.io/badge/CX_Count-1%2C948-blue)
![Qubit Width](https://img.shields.io/badge/Width-18_Qubits-orange)
![Verification](https://img.shields.io/badge/Verification-PASSED_(100%25)-success)

This repository contains the winning/champion implementation for the **Classiq Quantum Circuit Challenge 2026**, synthesizing and optimizing an exact quantum phase oracle for the 64×64 pixel Classiq logo under strict hardware constraints (Width ≤ 18 qubits, basis gates: `['u3', 'cx']`).

---

## 📊 Final Performance Metrics

| Metric | Baseline | Champion | Total Improvement |
| :--- | :--- | :--- | :--- |
| **Circuit Depth** | 5,329 | **2,959** | **-44.47%** (-2,370 depth) |
| **CX Gate Count** | 3,502 | **1,948** | **-44.37%** (-1,554 CX) |
| **Total Gate Count**| 7,000+ | **3,864** | **-44.8%** |
| **Qubit Width** | 18 qubits | **18 qubits** | **100% compliant** |
| **Correctness** | 100% | **100% Exact** | $E_{\text{max}} < 10^{-15}$ |

---

## 📁 Repository Structure

```
├── README.md                                 # Root project documentation
├── QuantumCircuitChallenge2026/
│   ├── submission.qasm                       # Final optimized QASM 2.0 file
│   ├── generate_best_submission.py           # End-to-end synthesizer & optimizer
│   ├── verify_submission.py                  # Unitary & phase oracle verifier
│   ├── OPTIMIZATION_DASHBOARD.md             # Complete step-by-step optimization logs
│   ├── FINAL_REPORT.md                       # Comprehensive engineering post-mortem
│   ├── submission_package/                   # Standalone submission bundle
│   │   ├── submission.qasm
│   │   ├── generate_best_submission.py
│   │   ├── verify_submission.py
│   │   └── OPTIMIZATION_DASHBOARD.md
```

---

## 🛠️ Key Architectural Innovations

### 1. Predicate Caching via Nested Closures
Arithmetic carry-chains for 6-bit numerical range checks (e.g. `50 <= x <= 60`) are computationally heavy. Rather than evaluating conditions redundantly across disconnected gates, we nested conditional sub-checks inside continuous range closures:
```python
def d1_50_60_body():
    control(y == 37, lambda: phase(pi))
    control(y == 38, lambda: phase(pi))
    control(y == 44, lambda: phase(pi))
    control(y == 45, lambda: phase(pi))

control((x >= 50) & (x <= 60), d1_50_60_body)
```
This forces the compiler to materialize the comparator predicate into a borrowable scratchpad qubit once, reusing it across four subsequent conditional phase gates.

### 2. Commutative Region Reordering for Gate Cancellation
Because phase operations commute ($[U_1, U_2] = 0$), the geometric regions forming the logo can be evaluated in any order. By analyzing multi-controlled Toffoli ladder structures, we sequenced the evaluation order:
$$\text{Square } S \longrightarrow D_2 \text{ (Core} \to X\text{-edges} \to Y\text{-edges)} \longrightarrow D_1 \text{ (Shells} \to \text{Bar)}$$
This spatial ordering maximizes the overlap of adjacent multi-qubit controls, allowing PyTket's peephole pass to cancel hundreds of redundant $CX$ pairs across region boundaries.

### 3. Hierarchical Control Optimization & Pass Pipelines
- **Classiq Engine:** Synthesis with `OptimizationParameter.DEPTH` and `max_width=18`.
- **Transpilation:** Classiq `INTENSIVE` transpilation targeting `['u3', 'cx']`.
- **Topological Optimization:** PyTket `FullPeepholeOptimise` and `OptimisePhaseGadgets` passes to eliminate phase gadgets and redundant single-qubit rotations.

---

## 🚀 Quick Start & Reproduction

### Prerequisites
Create a Python 3.10+ virtual environment and install the required dependencies:
```bash
pip install classiq pytket pytket-qiskit numpy
```

### 1. Generate Champion Circuit
Run the master generation script to synthesize and optimize the QASM circuit from scratch:
```bash
python QuantumCircuitChallenge2026/generate_best_submission.py
```
This will output the transpiled `submission.qasm` matching Depth **2,959** and CX **1,948**.

### 2. Verify Exact Correctness
Run the verification suite across arbitrary quantum superpositions and basis states:
```bash
python QuantumCircuitChallenge2026/verify_submission.py
```

Expected output:
```
==================================================
VERIFICATION REPORT
==================================================
State 1 Max Error: 3.62e-16 | Ancilla Error: 2.26e-16 | PASSED
State 2 Max Error: 2.91e-16 | Ancilla Error: 1.84e-16 | PASSED
State 3 Max Error: 3.14e-16 | Ancilla Error: 2.11e-16 | PASSED
==================================================
ALL CHECKS PASSED: Circuit is 100% correct!
==================================================
```

---

## 📜 License
This project is licensed under the MIT License.
