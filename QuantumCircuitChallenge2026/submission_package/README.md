# Classiq Quantum Circuit Challenge 2026 - Submission Package

This directory contains the standalone submission bundle for the **Classiq Quantum Circuit Challenge 2026**.

## 📊 Final Performance Metrics
- **Circuit Depth:** **2,959** (-44.47% reduction from baseline)
- **CX Count:** **1,948** (-44.37% reduction from baseline)
- **Total Gates:** **3,864**
- **Qubit Width:** **18 qubits** (12 data qubits + 6 ancillas)
- **Basis Gates:** `u3`, `cx` only
- **Verification:** **100% Exact** (Max Error $< 10^{-15}$)

---

## 📦 Package Contents

1. **`submission.qasm`**: The final optimized OpenQASM 2.0 quantum phase oracle circuit.
2. **`generate_best_submission.py`**: Complete Python pipeline to regenerate and re-optimize the circuit from scratch using Classiq + PyTket.
3. **`verify_submission.py`**: Full unitary and phase verification script validating statevectors and ancilla uncomputation.
4. **`OPTIMIZATION_DASHBOARD.md`**: Complete log of all 15 optimization stages, metrics, and ablation studies.

---

## 🚀 Reproduction & Verification Instructions

### 1. Verify Pre-Synthesized Circuit
```bash
python verify_submission.py
```

### 2. Regenerate Circuit from Source
```bash
python generate_best_submission.py
```
This executes the compiler-managed predicate caching synthesis, intensive transpilation, and PyTket peephole optimization passes, writing the resulting circuit to `submission.qasm`.
