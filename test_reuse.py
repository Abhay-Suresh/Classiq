import classiq
from classiq import *
from classiq.qmod.symbolic import pi

classiq.authenticate()

GRID_SIZE = 64
COORD_BITS = 6

@qperm
def logo_phase_oracle(x: Const[QNum], y: Const[QNum]) -> None:
    # Test sharing an intermediate expression
    is_S_x = (x >= 2) & (x <= 26)
    
    # We use it twice
    control(is_S_x & (y >= 29) & (y <= 38), lambda: phase(pi))
    control(is_S_x & (y >= 44) & (y <= 53), lambda: phase(pi))

@qfunc
def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
    allocate(x)
    allocate(y)
    hadamard_transform(x)
    hadamard_transform(y)
    logo_phase_oracle(x, y)

print("Synthesizing without reuse...")
baseline_constraints = Constraints(optimization_parameter=OptimizationParameter.DEPTH, max_width=18)
model = create_model(main, constraints=baseline_constraints)
try:
    qprog = synthesize(model)
    candidate_qasm = export(qprog, TargetLanguage.QASM2)
    lines = candidate_qasm.splitlines()
    cand = "\n".join(l for i, l in enumerate(lines) if not (l.lstrip().startswith("hadamard") and "q[" in l))
    from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings
    transpiled = classiq.transpile(quantum_program_from_qasm(cand), preferences=Preferences(transpilation_option=TranspilationOption.AUTO_OPTIMIZE, custom_hardware_settings=CustomHardwareSettings(basis_gates=["u3", "cx"])))
    metrics = classiq.get_transpiled_circuit_metrics(transpiled)
    print(f"Depth = {metrics.depth}, CX = {metrics.count_ops.get('cx', 0)}")
except Exception as e:
    print("Error:", e)

