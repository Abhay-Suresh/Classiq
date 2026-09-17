import numpy as np
from sympy.logic import simplify_logic
from sympy import symbols, Or, And, Not

# Read the minterms
with open("minterms.txt", "r") as f:
    minterms = [line.strip() for line in f.readlines()]

print(f"Loaded {len(minterms)} minterms")

# Convert to integers (LSB is bit 0)
minterm_ints = []
for m in minterms:
    m_reversed = m[::-1]
    minterm_ints.append(int(m_reversed, 2))

print(f"Converted to integers, range: {min(minterm_ints)} to {max(minterm_ints)}")

# Since sympy can't handle 12 variables efficiently, let's try a different approach
# Instead of full minimization, let's analyze bit patterns

# Bit analysis: For each bit position (0-11), see if it's mostly 1 or mostly 0
bit_counts = [0] * 12
for m in minterm_ints:
    for i in range(12):
        if (m >> i) & 1:
            bit_counts[i] += 1

print("\nBit distribution across all minterms:")
for i in range(12):
    if i < 6:
        bit_name = f"x{i}"
    else:
        bit_name = f"y{i-6}"
    print(f"  {bit_name}: {bit_counts[i]:4d}/1097 ({bit_counts[i]/1097*100:.1f}%)")

# Let's look for simple patterns: For y=39-43 (merged rectangle), see bit patterns
print("\n\nPatterns for merged rectangle (y=39-43):")
y_range = [39, 40, 41, 42, 43]
for y_val in y_range:
    bits = f"{y_val:06b}"
    print(f"  y={y_val:2d}: {bits} (y5..y0)")

# Since sympy might not handle 12 variables, let's write a custom heuristic:
# For each y group, create a simplified condition

print("\n\nAnalyzing grouped bit patterns...")
