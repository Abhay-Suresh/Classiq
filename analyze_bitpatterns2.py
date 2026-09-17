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

# Collect all black pixels with their bit patterns
black_pixels = []
for y in range(64):
    for x in range(64):
        if logo_pixel(x, y):
            black_pixels.append((x, y, f"{x:06b}", f"{y:06b}"))

print(f"Total black pixels: {len(black_pixels)}")

# Strategy: Group by Y ranges that share bit patterns
# Key observation from analysis:
# - y=39,40,41,42,43: all x in 2..61 → one big rectangle!
# - y=11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27: D2 circle
# - y=29..38: S square (x=2..26) with some D1 overlaps
# - y=44..53: S square (x=2..26) with some D1 overlaps

# Let's design the bitwise conditions:
# 1. y=39-43: y[5:2] = 00100 (bits 5,4,3,2 are 0,0,1,0)
#    Actually y=39 = 100111, y=43 = 101011
#    y[5] = 1, y[4] = 0, y[3] = 0 or 1, y[2] = 0 or 1

# For y in [39,43]: y = 10xxxx where 111 <= xxx <= 1011
# y=39 = 100111, y=40 = 101000, y=41 = 101001, y=42 = 101010, y=43 = 101011
# y[5]=1, y[4]=0, and y in [7,11] for lower 6 bits... wait that's not right.

# Let me check: y=39 = 0b100111, y=43 = 0b101011
# y[5]=1, y[4]=0 for both
# Lower 4 bits: 39=0111, 40=1000, 41=1001, 42=1010, 43=1011
# So for y in [39,43]: y[5]=1, y[4]=0, and y[3:0] in [7,11]
# y[3:0] >= 7 and y[3:0] <= 11 is (y & 15) >= 7 & (y & 15) <= 11

print("\n=== Key Bit Patterns ===")

# Pattern 1: y in [39,43], x in [2,61] - the big merged rectangle
# y=39 = 0b100111, y=43 = 0b101011
# y[5]=1, y[4]=0, y[3]=0 or 1, y[2]=0 or 1, y[1:0] vary
# Condition: y[5]=1, y[4]=0, y[3:0] in [7,11]
# y[3:0] >= 7 means (y & 15) >= 7, i.e., y[3]=1 and y[2:0] any, OR y[3]=0 and y[2:0] = 111
# y[3:0] <= 11 means (y & 15) <= 11, i.e., y[3]=0, OR y[3]=1 and y[2:0] <= 011

# For [39,43]: y = 0b10 + anything where lower 4 bits in [0111, 1011]
# Let's check: y=39, y=43 share y[5:4] = 10
# y[5:4] = 10 means (y & 48) == 32

print("Pattern 1: y in [39,43] using y & 48 == 32")
for y in range(39, 44):
    print(f"  y={y:2d}: y & 48 = {y & 48:2d}, expected 32, match = {(y & 48) == 32}")

# Pattern 2: y in [11,27] (D2 circle)
# y=11 = 0b001011, y=27 = 0b011011
# y[5:4] = 00 or 01
# y[5] = 0 for y < 32, so y=11..27 all have y[5]=0
# Let's use y[5]=0 and y >= 11 and y <= 27
print("\nPattern 2: y in [11,27] using y[5]=0")
for y in [11, 27]:
    print(f"  y={y:2d}: y < 32 = {y < 32}")

# Pattern 3: y in [29,53] (Square S)
# y=29 = 0b011101, y=53 = 0b110101
# y[5:4] varies: 29=01, 53=11
# Not a simple bit pattern!
# But we can split: y in [29,38] or y in [44,53]

print("\nPattern 3: Square S split into parts")
# y in [29,38]: y=011101 to y=100110
# y[5:4] = 01 or 10
# Hmm, this crosses the y[4] boundary too.

# Let's try a different approach: use ranges with AND operations
# (y >= 29) & (y <= 53) is the square range
# But we want bitwise!
# y >= 29 means y > 28 = 0b011100
# y <= 53 means y < 54 = 0b110110

# For bitwise, let's check what y values in each group share
print("\nChecking if we can group D2 by y[5:3] = 001, 010, 011")
for y_high in [1, 2, 3]:  # y[5:3] = 001, 010, 011
    mask = 0b111000  # mask for y[5:3]
    for y in range(64):
        if (y & mask) == (y_high << 3):
            if (11 <= y <= 27):  # D2 range
                print(f"  y={y:2d}: y & {mask:06b} = {y & mask:06b} = {y_high << 3}")

print("\nFor y=39-43 (merged rectangle):")
for y in range(39, 44):
    print(f"  y={y:2d}: {y:06b}")

# y=39 = 100111
# y=40 = 101000
# y=41 = 101001
# y=42 = 101010
# y=43 = 101011
# Common pattern: y[5]=1, y[4]=0
# Lower 4 bits vary from 0111 to 1011
# (y & 48) == 32 means y[5]=1, y[4]=0
# AND (y & 15) >= 7 means lower 4 bits >= 0111
# AND (y & 15) <= 11 means lower 4 bits <= 1011

print("\nFor y=39-43: (y & 48) == 32 AND (y & 15) in [7,11]")
for y in range(39, 44):
    lower4 = y & 15
    print(f"  y={y:2d}: lower 4 bits = {lower4:04b} = {lower4}, in [7,11]? {7 <= lower4 <= 11}")

