# Classiq Quantum Circuit Challenge 2026 - Submission Package

This directory contains the standalone submission bundle for the **Classiq Quantum Circuit Challenge 2026**.

## 📊 Final Performance Metrics
- **Circuit Depth:** **1,597** (70.0% reduction from baseline 5,329)
- **CX Count:** **1,557** (55.5% reduction from baseline 3,502)
- **Qubit Width:** **18 qubits** (12 data qubits + 6 ancillas)
- **Basis Gates:** `u3`, `cx` only
- **Verification:** **100% Exact** (Max Error $< 2.53 \times 10^{-16}$, Ancilla leakage $< 1.32 \times 10^{-16}$)

---

## 📦 Package Contents

1. **`submission.qasm`**: The final optimized OpenQASM 2.0 quantum phase oracle circuit.
2. **`verify_submission.py`**: Full unitary and phase verification script validating statevectors and ancilla uncomputation.
3. **`optimized_esop_60.json`**: The 60-cube minimal exact ESOP cover over the 12 coordinate variables.
4. **`OPTIMIZATION_DASHBOARD.md`**: Complete log of all optimization stages, metrics, and ablation studies.

---

## 🚀 Reproduction & Verification Instructions

### 1. Verify Pre-Synthesized Circuit
```bash
python verify_submission.py
```

### 2. Regenerate Circuit from Source
The full pipeline lives in the notebook `classiq-challenge-baseline (1).ipynb` (in the parent directory). Run it end-to-end to regenerate the circuit: it loads the 60-cube ESOP, builds the literal-scored prefix trie, compiles with Classiq depth optimization, applies INTENSIVE transpilation, and iterates PyTket passes until convergence — writing the result to `submission.qasm`.
