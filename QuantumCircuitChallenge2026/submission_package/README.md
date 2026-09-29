# Classiq Quantum Circuit Challenge 2026 - Submission Package

This directory contains the standalone submission bundle for the **Classiq Quantum Circuit Challenge 2026**.

## 📊 Final Performance Metrics
- **Circuit Depth:** **1,664** (68.8% reduction from baseline 5,329)
- **CX Count:** **1,595** (54.5% reduction from baseline 3,502)
- **Qubit Width:** **18 qubits** (12 data qubits + 6 ancillas)
- **Basis Gates:** `u3`, `cx` only
- **Verification:** **100% Exact** (Max Error $< 2.06 \times 10^{-16}$, Ancilla leakage $< 1.59 \times 10^{-16}$)

---

## 📦 Package Contents

1. **`submission.qasm`**: The final optimized OpenQASM 2.0 quantum phase oracle circuit.
2. **`generate_best_submission.py`**: Complete Python pipeline to regenerate and re-optimize the circuit from scratch using Classiq + PyTket (Vectorized GF(2) ESOP + Literal-Scored Prefix Trie Factorization).
3. **`verify_submission.py`**: Full unitary and phase verification script validating statevectors and ancilla uncomputation.
4. **`OPTIMIZATION_DASHBOARD.md`**: Complete log of all optimization stages, metrics, and ablation studies.

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
This executes the 61-cube ESOP loader, prefix-trie QMOD generation, intensive Classiq transpilation, and PyTket peephole optimization passes, writing the resulting circuit to `submission.qasm`.
