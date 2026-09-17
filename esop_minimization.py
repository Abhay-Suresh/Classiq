from sympy.logic import simplify_logic
from sympy import symbols, Or, And, Not
import itertools

# Read the minterms
with open("minterms.txt", "r") as f:
    minterms = [line.strip() for line in f.readlines()]

print(f"Loaded {len(minterms)} minterms")

# Convert to integers for sympy
minterm_ints = []
for m in minterms:
    m_reversed = m[::-1]
    minterm_ints.append(int(m_reversed, 2))

print(f"Converted to integers, range: {min(minterm_ints)} to {max(minterm_ints)}")

# Define symbols for 12 variables
x = [symbols(f'x{i}') for i in range(6)]
y = [symbols(f'y{i}') for i in range(6)]

# Build the ON-set using sympy's SOP form directly
# sympy.simplify_logic accepts a list of minterm integers
print("\nUsing simplify_logic directly with minterm list...")
simplified = simplify_logic(minterm_ints, 12, form='sop')

print(f"Simplified!")
print(f"\nSimplified expression:\n{simplified}")

# Save to file
with open("simplified_sop.txt", "w") as f:
    f.write(str(simplified))
print(f"\nSaved to simplified_sop.txt")

