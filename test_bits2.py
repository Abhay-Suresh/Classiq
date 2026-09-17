import classiq
from classiq import *
from classiq.qmod.symbolic import pi

classiq.authenticate()

GRID_SIZE = 64
COORD_BITS = 6

@qperm
def logo_phase_oracle(x: Const[QNum], y: Const[QNum]) -> None:
    # Cast to bit arrays so we can do bitwise logic natively
    # y in [32, 47] is y[5]==1 and y[4]==0
    
    # In Qmod, we can do QArray operations or use classical expressions?
    # No, we can just do comparisons directly. 
    # But wait, QNum comparators are already very optimized.
    
    # Let's test the baseline rectangle 14
    control((x >= 2) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

@qfunc
def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
    allocate(x)
    allocate(y)
    hadamard_transform(x)
    hadamard_transform(y)
    logo_phase_oracle(x, y)

print("Synthesizing Baseline Rect...")
baseline_constraints = Constraints(optimization_parameter=OptimizationParameter.DEPTH, max_width=18)
model = create_model(main, constraints=baseline_constraints)
try:
    qprog = synthesize(model)
    print("SUCCESS!")
    
    candidate_qasm = export(qprog, TargetLanguage.QASM2)
    # Remove hadamards
    lines = candidate_qasm.splitlines()
    prep = {i for i, l in enumerate(lines) if l.lstrip().startswith("hadamard") and "q[" in l}
    cand = "\n".join(l for i, l in enumerate(lines) if i not in prep)
    
    from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings
    transpiled = classiq.transpile(
        quantum_program_from_qasm(cand),
        preferences=Preferences(
            transpilation_option=TranspilationOption.AUTO_OPTIMIZE,
            custom_hardware_settings=CustomHardwareSettings(basis_gates=["u3", "cx"]),
        )
    )
    metrics = classiq.get_transpiled_circuit_metrics(transpiled)
    print(f"Depth = {metrics.depth}, CX = {metrics.count_ops.get('cx', 0)}")
except Exception as e:
    print("Error:", e)
