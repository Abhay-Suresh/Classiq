import classiq
from classiq import *
from classiq.qmod.symbolic import pi

classiq.authenticate()

GRID_SIZE = 64
COORD_BITS = 6

@qperm
def logo_phase_oracle_optimized(x: Const[QNum], y: Const[QNum]) -> None:
    # Use standard comparisons for the merged rectangle to avoid high qubit counts
    control((x >= 2) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    
    # Square S: x in [2,26]
    is_S_x = (x >= 2) & (x <= 26)
    
    # S bottom: y in [29,38]
    control(is_S_x & (y >= 29) & (y <= 38), lambda: phase(pi))
    
    # S top: y in [44,53]  
    control(is_S_x & (y >= 44) & (y <= 53), lambda: phase(pi))
    
    # D2 Circle (y=11-27)
    control((y == 11) & (x >= 38) & (x <= 42), lambda: phase(pi))
    control((y == 12) & (x >= 36) & (x <= 44), lambda: phase(pi))
    control((y >= 13) & (y <= 14) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 15) & (y <= 16) & (x >= 33) & (x <= 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x >= 32) & (x <= 48), lambda: phase(pi))
    control((y >= 22) & (y <= 23) & (x >= 33) & (x <= 47), lambda: phase(pi))
    control((y >= 24) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y == 26) & (x >= 36) & (x <= 44), lambda: phase(pi))
    control((y == 27) & (x >= 38) & (x <= 42), lambda: phase(pi))
    
    # D1 Circle (y=35-38, 44-47)
    control((y == 35) & (x >= 53) & (x <= 57), lambda: phase(pi))
    control((y == 36) & (x >= 51) & (x <= 59), lambda: phase(pi))
    control((y >= 37) & (y <= 38) & (x >= 50) & (x <= 60), lambda: phase(pi))
    control((y >= 44) & (y <= 45) & (x >= 50) & (x <= 60), lambda: phase(pi))
    control((y == 46) & (x >= 51) & (x <= 59), lambda: phase(pi))
    control((y == 47) & (x >= 53) & (x <= 57), lambda: phase(pi))

@qfunc
def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
    allocate(x)
    allocate(y)
    hadamard_transform(x)
    hadamard_transform(y)
    logo_phase_oracle_optimized(x, y)

print("Synthesizing solution with shared variables...")
baseline_constraints = Constraints(
    optimization_parameter=OptimizationParameter.DEPTH,
    max_width=18,
)
model = create_model(main, constraints=baseline_constraints)
write_qmod(model, "submission")

try:
    qprog = synthesize(model)
    print("Synthesis succeeded!")
    
    raw_qasm = export(qprog, TargetLanguage.QASM2)
    raw_lines = raw_qasm.splitlines()

    preparation_indices = {
        index for index, line in enumerate(raw_lines)
        if line.lstrip().startswith("hadamard_transform_") and "q[" in line
    }
    candidate_qasm = "\n".join(
        line for index, line in enumerate(raw_lines) if index not in preparation_indices
    )
    candidate_qprog = quantum_program_from_qasm(candidate_qasm)

    from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings
    transpiled = classiq.transpile(
        candidate_qprog,
        preferences=Preferences(
            transpilation_option=TranspilationOption.AUTO_OPTIMIZE,
            custom_hardware_settings=CustomHardwareSettings(basis_gates=["u3", "cx"]),
        ),
    )
    
    submission_qasm = export(
        transpiled,
        TargetLanguage.QASM2,
        transpilation_config=TranspilationConfig(basis_gates=["u3", "cx"]),
    )
    
    with open("submission.qasm", "w", encoding="utf-8") as f:
        f.write(submission_qasm)
    
    metrics = classiq.get_transpiled_circuit_metrics(transpiled)
    print(f"\nRESULTS:")
    print(f"Width:    {metrics.width}")
    print(f"Depth:    {metrics.depth}")
    print(f"CX count: {metrics.count_ops.get('cx', 0)}")
    print(f"\nBaseline: depth=5329, CX=3502")
    if metrics.depth < 5329:
        print(f"IMPROVEMENT: Depth reduced by {5329 - metrics.depth}")
    else:
        print(f"No improvement in depth.")
except Exception as e:
    print("Error during synthesis:", e)
