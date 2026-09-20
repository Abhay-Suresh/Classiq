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

@qfunc
def logo_phase_oracle_tier5_best(x: Const[QNum], y: Const[QNum]) -> None:
    # Tier 5.2: D2 (Core -> X -> Y) Then D1 (Shells -> Bar) (Depth 2959, CX 1948 - NEW CHAMPION)

    # 1. Main Square S
    control((x >= 2) & (x <= 26) & (y >= 29) & (y <= 53), lambda: phase(pi))

    # 2. D2 Core
    control((x >= 34) & (x <= 46) & (y >= 13) & (y <= 25), lambda: phase(pi))

    # 3. D2 X-dominant edges
    def d2_x36_44_body():
        control(y == 12, lambda: phase(pi))
        control(y == 26, lambda: phase(pi))
    control((x >= 36) & (x <= 44), d2_x36_44_body)

    def d2_x38_42_body():
        control(y == 11, lambda: phase(pi))
        control(y == 27, lambda: phase(pi))
    control((x >= 38) & (x <= 42), d2_x38_42_body)

    # 4. D2 Y-dominant edges
    def d2_y17_21_body():
        control(x == 32, lambda: phase(pi))
        control(x == 48, lambda: phase(pi))
    control((y >= 17) & (y <= 21), d2_y17_21_body)

    def d2_y15_23_body():
        control(x == 33, lambda: phase(pi))
        control(x == 47, lambda: phase(pi))
    control((y >= 15) & (y <= 23), d2_y15_23_body)

    # 5. D1 Shells (placed before Bar for optimal peephole rotation and CX cancellation)
    def d1_50_60_body():
        control(y == 37, lambda: phase(pi))
        control(y == 38, lambda: phase(pi))
        control(y == 44, lambda: phase(pi))
        control(y == 45, lambda: phase(pi))
    control((x >= 50) & (x <= 60), d1_50_60_body)

    def d1_51_59_body():
        control(y == 36, lambda: phase(pi))
        control(y == 46, lambda: phase(pi))
    control((x >= 51) & (x <= 59), d1_51_59_body)

    def d1_53_57_body():
        control(y == 35, lambda: phase(pi))
        control(y == 47, lambda: phase(pi))
    control((x >= 53) & (x <= 57), d1_53_57_body)

    # 6. Main D1 Bar
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

@qfunc
def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
    allocate(x)
    allocate(y)
    hadamard_transform(x)
    hadamard_transform(y)
    logo_phase_oracle_tier5_best(x, y)

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
