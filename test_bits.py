import classiq
from classiq import *
from classiq.qmod.symbolic import pi

classiq.authenticate()

GRID_SIZE = 64
COORD_BITS = 6

@qperm
def logo_phase_oracle(x: Const[QNum], y: Const[QNum]) -> None:
    # Test bit access: y in 32..47 is y[5]==1 and y[4]==0
    # QNum in Qmod supports bit access: x[i]
    # Let's try to parse the 6 bits
    # Qmod might not allow single bit indexing on Const[QNum], or it gives QBit.
    # We can check y >= 32 & y <= 47 vs bitwise
    
    # Try using bitwise AND: y & 48 == 32 (which means y5=1, y4=0)
    # y = ... _ _ 1 0 _ _ _ _ 
    # 48 is 110000 in binary
    # 32 is 100000 in binary
    cond = (y & 48) == 32
    control(cond, lambda: phase(pi))

@qfunc
def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
    allocate(x)
    allocate(y)
    hadamard_transform(x)
    hadamard_transform(y)
    logo_phase_oracle(x, y)

print("Synthesizing Bitwise...")
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
