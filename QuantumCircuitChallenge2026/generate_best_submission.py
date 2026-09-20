import re
import warnings
from pathlib import Path
import numpy as np
import classiq
from classiq import *
from classiq.qmod.symbolic import pi
from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings
from pytket.qasm import circuit_from_qasm_str, circuit_to_qasm_str
from pytket.passes import FullPeepholeOptimise

GRID_SIZE = 64
COORD_BITS = 6

@qperm
def logo_phase_oracle(x: Const[QNum], y: Const[QNum]) -> None:
    is_S_x = (x >= 2) & (x <= 26)

    # 1. Largest regions
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # 2. D1 outer shells with predicate caching (nesting)
    def d1_50_60_body():
        control((y >= 37) & (y <= 38), lambda: phase(pi))
        control((y >= 44) & (y <= 45), lambda: phase(pi))
        
    control((x >= 50) & (x <= 60), d1_50_60_body)

    control((x >= 51) & (x <= 59) & ((y == 36) | (y == 46)), lambda: phase(pi))
    control((x >= 53) & (x <= 57) & ((y == 35) | (y == 47)), lambda: phase(pi))

    # 3. D2 REVERSE edges [c4, c3, c2, c1]
    control((y >= 17) & (y <= 21) & ((x == 32) | (x == 48)), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & ((x == 33) | (x == 47)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

@qfunc
def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
    allocate(x)
    allocate(y)
    hadamard_transform(x)
    hadamard_transform(y)
    logo_phase_oracle(x, y)

print("Synthesizing best nested model...")
constraints = Constraints(optimization_parameter=OptimizationParameter.DEPTH, max_width=18)
model = create_model(main, constraints=constraints)
write_qmod(model, "submission")
qprog = synthesize(model)

raw_qasm = export(qprog, TargetLanguage.QASM2)
raw_lines = raw_qasm.splitlines()
preparation_indices = {
    index for index, line in enumerate(raw_lines)
    if line.lstrip().startswith("hadamard_transform_") and "q[" in line
}
candidate_qasm = "\n".join(line for index, line in enumerate(raw_lines) if index not in preparation_indices)
candidate_qprog = quantum_program_from_qasm(candidate_qasm)

print("Transpiling with Classiq INTENSIVE...")
transpiled = classiq.transpile(
    candidate_qprog,
    preferences=Preferences(
        transpilation_option=TranspilationOption.INTENSIVE,
        custom_hardware_settings=CustomHardwareSettings(basis_gates=["u3", "cx"]),
    ),
)

raw_submission_qasm = export(
    transpiled, TargetLanguage.QASM2,
    transpilation_config=TranspilationConfig(transpilation_level=TranspilationOption.INTENSIVE, basis_gates=["u3", "cx"]),
)

print("Applying pytket FullPeepholeOptimise...")
tk_circ = circuit_from_qasm_str(raw_submission_qasm)
FullPeepholeOptimise().apply(tk_circ)
optimized_qasm = circuit_to_qasm_str(tk_circ)

Path("submission.qasm").write_text(optimized_qasm, encoding="utf-8")
final_metrics = classiq.get_transpiled_circuit_metrics(classiq.quantum_program_from_qasm(optimized_qasm))

print("\n" + "="*50)
print(f"NEW SUBMISSION METRICS:")
print(f"Depth    = {final_metrics.depth}")
print(f"CX count = {final_metrics.count_ops.get('cx', 0)}")
print(f"Width    = {final_metrics.width}")
print("="*50)
