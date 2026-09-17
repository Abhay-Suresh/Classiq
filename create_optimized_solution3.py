import classiq
from classiq import *
from classiq.qmod.symbolic import pi

classiq.authenticate()

GRID_SIZE = 64
COORD_BITS = 6

@qperm
def logo_phase_oracle_optimized(x: Const[QNum], y: Const[QNum]) -> None:
    # Pre-compute all shared X conditions
    # Square S
    is_S_x = (x >= 2) & (x <= 26)
    
    # D2 Circle shared X conditions
    is_d2_x_38_42 = (x >= 38) & (x <= 42)
    is_d2_x_36_44 = (x >= 36) & (x <= 44)
    is_d2_x_34_46 = (x >= 34) & (x <= 46)
    is_d2_x_33_47 = (x >= 33) & (x <= 47)
    is_d2_x_32_48 = (x >= 32) & (x <= 48)
    
    # D1 Circle shared X conditions
    is_d1_x_53_57 = (x >= 53) & (x <= 57)
    is_d1_x_51_59 = (x >= 51) & (x <= 59)
    is_d1_x_50_60 = (x >= 50) & (x <= 60)
    
    # 1. Merged rectangle
    control((x >= 2) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))
    
    # 2. Square S
    control(is_S_x & (y >= 29) & (y <= 38), lambda: phase(pi))
    control(is_S_x & (y >= 44) & (y <= 53), lambda: phase(pi))
    
    # 3. D2 Circle
    control((y == 11) & is_d2_x_38_42, lambda: phase(pi))
    control((y == 12) & is_d2_x_36_44, lambda: phase(pi))
    control((y >= 13) & (y <= 14) & is_d2_x_34_46, lambda: phase(pi))
    control((y >= 15) & (y <= 16) & is_d2_x_33_47, lambda: phase(pi))
    control((y >= 17) & (y <= 21) & is_d2_x_32_48, lambda: phase(pi))
    control((y >= 22) & (y <= 23) & is_d2_x_33_47, lambda: phase(pi))
    control((y >= 24) & (y <= 25) & is_d2_x_34_46, lambda: phase(pi))
    control((y == 26) & is_d2_x_36_44, lambda: phase(pi))
    control((y == 27) & is_d2_x_38_42, lambda: phase(pi))
    
    # 4. D1 Circle
    control((y == 35) & is_d1_x_53_57, lambda: phase(pi))
    control((y == 36) & is_d1_x_51_59, lambda: phase(pi))
    control((y >= 37) & (y <= 38) & is_d1_x_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_x_50_60, lambda: phase(pi))
    control((y == 46) & is_d1_x_51_59, lambda: phase(pi))
    control((y == 47) & is_d1_x_53_57, lambda: phase(pi))

@qfunc
def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
    allocate(x)
    allocate(y)
    hadamard_transform(x)
    hadamard_transform(y)
    logo_phase_oracle_optimized(x, y)

print("Synthesizing with maximum predicate sharing...")
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
