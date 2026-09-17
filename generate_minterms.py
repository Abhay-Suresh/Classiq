import numpy as np

GRID_SIZE = 64

def logo_pixel(x: int, y: int) -> bool:
    return (
        (2 <= x <= 26 and 29 <= y <= 53)
        or (26 <= x <= 49 and 39 <= y <= 43)
        or (x - 55) ** 2 + (y - 41) ** 2 <= 42
        or (x - 40) ** 2 + (y - 19) ** 2 <= 72
    )

# Collect all black pixel minterms
# Format: 12-bit binary string where bits are x[5:0] concatenated with y[5:0]
# Using little-endian: index = x + y*64

minterms = []
for y in range(64):
    for x in range(64):
        if logo_pixel(x, y):
            # Create 12-bit representation
            # Convention: bits 0-5 are x[0:5], bits 6-11 are y[0:5]
            # We'll use big-endian for readability: x5 x4 x3 x2 x1 x0 y5 y4 y3 y2 y1 y0
            minterm = f"{x:06b}{y:06b}"
            minterms.append(minterm)

print(f"Total minterms: {len(minterms)}")
print(f"\nFirst 10 minterms:")
for m in minterms[:10]:
    x_val = int(m[:6], 2)
    y_val = int(m[6:], 2)
    print(f"  {m} (x={x_val}, y={y_val})")

# Save to file in ESPRESSO format
with open("minterms.pla", "w") as f:
    f.write(".i 12\n")
    f.write(f".o 1\n")
    f.write(f".p {len(minterms)}\n")
    for m in minterms:
        f.write(f"{m} 1\n")
    f.write(".e\n")

print(f"\nSaved minterms to minterms.pla in ESPRESSO format")

# Also save as simple list
with open("minterms.txt", "w") as f:
    for m in minterms:
        f.write(f"{m}\n")

print(f"Also saved to minterms.txt (simple list)")
