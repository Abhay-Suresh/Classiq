import numpy as np
from collections import defaultdict

GRID_SIZE = 64

def logo_pixel(x: int, y: int) -> bool:
    return (
        (2 <= x <= 26 and 29 <= y <= 53)
        or (26 <= x <= 49 and 39 <= y <= 43)
        or (x - 55) ** 2 + (y - 41) ** 2 <= 42
        or (x - 40) ** 2 + (y - 19) ** 2 <= 72
    )

# Collect all black pixels
black_pixels = []
for y in range(64):
    for x in range(64):
        if logo_pixel(x, y):
            black_pixels.append((x, y))

print(f"Total black pixels: {len(black_pixels)}")

# Analyze bit patterns
# Strategy: Group by high bits, then check low bits
# For y: bits are y5 y4 y3 y2 y1 y0
# For x: bits are x5 x4 x3 x2 x1 x0

# Group by y high 3 bits (y5, y4, y3)
y_groups = defaultdict(list)
for x, y in black_pixels:
    y_high = (y >> 3) & 0b111  # Top 3 bits of y
    y_groups[y_high].append((x, y))

print("\n=== Y High 3-bit Groups ===")
for y_high in sorted(y_groups.keys()):
    pixels = y_groups[y_high]
    y_values = sorted(set(y for _, y in pixels))
    y_range = f"{min(y_values)}..{max(y_values)}"
    print(f"y[5:3] = {y_high:03b} ({y_high}): {len(pixels)} pixels, y in {y_range}")

# For each y group, analyze x patterns
print("\n=== Analyzing X patterns per Y group ===")
for y_high in sorted(y_groups.keys()):
    pixels = y_groups[y_high]
    y_values = sorted(set(y for _, y in pixels))
    
    print(f"\ny[5:3] = {y_high:03b} ({y_high}), y range {min(y_values)}..{max(y_values)}:")
    
    # Group by y within this y_high group
    y_subgroups = defaultdict(list)
    for x, y in pixels:
        y_subgroups[y].append(x)
    
    for y_val in sorted(y_subgroups.keys()):
        x_vals = sorted(y_subgroups[y_val])
        x_ranges = []
        start = x_vals[0]
        end = x_vals[0]
        for x in x_vals[1:]:
            if x == end + 1:
                end = x
            else:
                x_ranges.append(f"{start}..{end}" if start != end else f"{start}")
                start = x
                end = x
        x_ranges.append(f"{start}..{end}" if start != end else f"{start}")
        print(f"  y={y_val:2d} ({y_val:06b}): x in {', '.join(x_ranges)}")

