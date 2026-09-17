import numpy as np

GRID_SIZE = 64

def logo_pixel(x: int, y: int) -> bool:
    return (
        (2 <= x <= 26 and 29 <= y <= 53)
        or (26 <= x <= 49 and 39 <= y <= 43)
        or (x - 55) ** 2 + (y - 41) ** 2 <= 42
        or (x - 40) ** 2 + (y - 19) ** 2 <= 72
    )

# 12 input bits: x0..x5, y0..y5
# total 4096 minterms
minterms = []
for y in range(64):
    for x in range(64):
        if logo_pixel(x, y):
            # 12-bit index: little-endian x (bits 0..5), y (bits 6..11)
            idx = x | (y << 6)
            minterms.append(idx)

print(f"Total minterms: {len(minterms)}")
