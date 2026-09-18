#!/usr/bin/env python3
"""
Test 10-Control Hybrid Geometry (merge Bar and D1 Core).
"""
import warnings
import classiq
from classiq import *
from classiq.qmod.symbolic import pi
from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings

warnings.filterwarnings("ignore")

COORD_BITS = 6

@qfunc
def main(x: Output[QNum[COORD_BITS]], y: Output[QNum[COORD_BITS]]) -> None:
    allocate(x)
    allocate(y)
    hadamard_transform(x)
    hadamard_transform(y)

    is_S_x = (x >= 2) & (x <= 26)

    # 1. Square S complete
    control(is_S_x & (y >= 29) & (y <= 53), lambda: phase(pi))

    # 2. Hybrid Bar and D1 core (Merged: x=27..61, y=39..43)
    # (Checking y=39..43 is Bar, y=39..43 is D1-core)
    control((x >= 27) & (x <= 61) & (y >= 39) & (y <= 43), lambda: phase(pi))

    # ... other D1 shells and D2 (using same as before) ...
    is_d1_50_60 = (x >= 50) & (x <= 60)
    is_d1_51_59 = (x >= 51) & (x <= 59)
    is_d1_53_57 = (x >= 53) & (x <= 57)

    control((y >= 37) & (y <= 38) & is_d1_50_60, lambda: phase(pi))
    control((y >= 44) & (y <= 45) & is_d1_50_60, lambda: phase(pi))
    control(is_d1_51_59 & ((y == 36) | (y == 46)), lambda: phase(pi))
    control(is_d1_53_57 & ((y == 35) | (y == 47)), lambda: phase(pi))

    # ... D2 ...
    control((y >= 13) & (y <= 25) & (x >= 34) & (x <= 46), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 33), lambda: phase(pi))
    control((y >= 15) & (y <= 23) & (x == 47), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 32), lambda: phase(pi))
    control((y >= 17) & (y <= 21) & (x == 48), lambda: phase(pi))
    control((x >= 36) & (x <= 44) & ((y == 12) | (y == 26)), lambda: phase(pi))
    control((x >= 38) & (x <= 42) & ((y == 11) | (y == 27)), lambda: phase(pi))

model = create_model(main, constraints=Constraints(
    optimization_parameter=OptimizationParameter.DEPTH, max_width=18))
qprog = synthesize(model)
# ... transpilation as before ...
transpiled = classiq.transpile(
    qprog,
    preferences=Preferences(
        transpilation_option=TranspilationOption.INTENSIVE,
        custom_hardware_settings=CustomHardwareSettings(basis_gates=['u3', 'cx']),
    ),
)
metrics = classiq.get_transpiled_circuit_metrics(transpiled)
print(f"DEPTH={metrics.depth}, CX={metrics.count_ops.get('cx', 0)}")
