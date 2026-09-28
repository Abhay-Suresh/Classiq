import numpy as np
from collections import Counter
import classiq
from classiq import *
from classiq.qmod.symbolic import pi
from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings
from classiq import Constraints, OptimizationParameter, Preferences, TranspilationConfig, TranspilationOption
from pytket.qasm import circuit_from_qasm_str, circuit_to_qasm_str
from pytket.passes import FullPeepholeOptimise, AutoRebase
from pytket.circuit import OpType

def logo_pixel(x: int, y: int) -> bool:
    return (
        (2 <= x <= 26 and 29 <= y <= 53)
        or (26 <= x <= 49 and 39 <= y <= 43)
        or (x - 55) ** 2 + (y - 41) ** 2 <= 42
        or (x - 40) ** 2 + (y - 19) ** 2 <= 72
    )

bitmap = np.zeros((64, 64), dtype=np.uint8)
for y in range(64):
    for x in range(64):
        if logo_pixel(x, y):
            bitmap[y, x] = 1

def pack_bits(arr): return np.packbits(arr).view(np.uint64)
target_packed = pack_bits(bitmap.flatten())

y_cubes, y_infos = [], []
for mask in range(64):
    for val in range(64):
        if (val & mask) != val: continue
        match = np.array([(y & mask) == val for y in range(64)], dtype=np.uint8)
        y_cubes.append(match)
        y_infos.append((mask, val))

x_cubes, x_infos = [], []
for mask in range(64):
    for val in range(64):
        if (val & mask) != val: continue
        match = np.array([(x & mask) == val for x in range(64)], dtype=np.uint8)
        x_cubes.append(match)
        x_infos.append((mask, val))

n_y, n_x = len(y_cubes), len(x_cubes)
subcubes_packed = np.zeros((n_y * n_x, 64), dtype=np.uint64)
subcube_info = []

idx = 0
for i in range(n_y):
    y_m, y_v = y_infos[i]
    for j in range(n_x):
        x_m, x_v = x_infos[j]
        subcubes_packed[idx] = np.packbits(np.outer(y_cubes[i], x_cubes[j]).flatten()).view(np.uint64)
        subcube_info.append((y_m, y_v, x_m, x_v))
        idx += 1

lut = np.array([bin(i).count('1') for i in range(256)], dtype=np.int32)
current_packed = target_packed.copy()
chosen_cubes = []
for step in range(150):
    u8 = current_packed.view(np.uint8)
    cur_w = int(lut[u8].sum())
    if cur_w == 0: break
    xor_arr = np.bitwise_xor(subcubes_packed, current_packed)
    weights = lut[xor_arr.view(np.uint8)].sum(axis=-1)
    best_idx = np.argmin(weights)
    chosen_cubes.append(subcube_info[best_idx])
    current_packed = current_packed ^ subcubes_packed[best_idx]

# Map each cube to a frozenset of literals
all_cubes = []
for ym, yv, xm, xv in chosen_cubes:
    lits = set()
    for i in range(6):
        if (ym >> i) & 1:
            lits.add(('y', i, (yv >> i)&1))
    for i in range(6):
        if (xm >> i) & 1:
            lits.add(('x', i, (xv >> i)&1))
    all_cubes.append(frozenset(lits))

print(f"Total initial cubes: {len(all_cubes)}")

class TrieNode:
    def __init__(self, lit=None):
        self.lit = lit # ('x'/'y', idx, val) or None
        self.is_terminal = False
        self.children = [] # List of TrieNode
        self.leaf_cubes = [] # List of frozenset of literals for remaining conditions

def build_proper_trie(cubes, min_freq=2):
    # Base cases
    if not cubes:
        return None

    # Check if there is an empty cube (means we apply phase right at this node)
    has_empty = frozenset() in cubes
    non_empty = [c for c in cubes if c != frozenset()]

    node = TrieNode()
    if has_empty:
        node.is_terminal = True

    if not non_empty:
        return node

    # Count frequencies of all literals in non_empty cubes
    counts = Counter()
    for c in non_empty:
        for lit in c:
            counts[lit] += 1

    best_lit, max_c = counts.most_common(1)[0]

    # If the most common literal is below threshold, just make all remaining into leaf cubes
    if max_c < min_freq:
        node.leaf_cubes = non_empty
        return node

    # Otherwise, split cubes into those that have best_lit and those that don't
    with_lit = []
    without_lit = []
    for c in non_empty:
        if best_lit in c:
            with_lit.append(c - {best_lit})
        else:
            without_lit.append(c)

    # Create child for with_lit
    child_node = build_proper_trie(with_lit, min_freq)
    child_node.lit = best_lit
    node.children.append(child_node)

    # Create child for without_lit if any
    if without_lit:
        other_child = build_proper_trie(without_lit, min_freq)
        # Note: other_child has lit=None because it does not require a condition on its own
        node.children.append(other_child)

    return node

trie_root = build_proper_trie(all_cubes, min_freq=2)

def count_trie_leaves(node):
    count = 1 if node.is_terminal else 0
    count += len(node.leaf_cubes)
    for c in node.children:
        count += count_trie_leaves(c)
    return count

print(f"Total leaves/cubes preserved: {count_trie_leaves(trie_root)} (should be {len(all_cubes)})")

def render_node(node, x, y):
    if node.is_terminal:
        phase(pi)

    for cube in node.leaf_cubes:
        conds = []
        for var, idx, val in cube:
            reg = x if var == 'x' else y
            conds.append(reg[idx] == val)
        if not conds:
            phase(pi)
        else:
            c = conds[0]
            for rest in conds[1:]:
                c = c & rest
            control(c, lambda: phase(pi))

    for child in node.children:
        if child.lit is not None:
            var, idx, val = child.lit
            reg = x if var == 'x' else y
            control(reg[idx] == val, lambda child=child: render_node(child, x, y))
        else:
            render_node(child, x, y)

@qfunc
def main(x: Output[QArray[QBit, 6]], y: Output[QArray[QBit, 6]]):
    allocate(6, x)
    allocate(6, y)
    hadamard_transform(x)
    hadamard_transform(y)
    render_node(trie_root, x, y)

constraints = Constraints(optimization_parameter=OptimizationParameter.DEPTH, max_width=18)
model = create_model(main, constraints=constraints)
qprog = synthesize(model)
raw_qasm = export(qprog, TargetLanguage.QASM2)
raw_lines = raw_qasm.splitlines()
candidate_qasm = "\n".join(line for index, line in enumerate(raw_lines)
                           if not (line.lstrip().startswith("hadamard_transform_") and "q[" in line))

transpiled = classiq.transpile(
    quantum_program_from_qasm(candidate_qasm),
    preferences=Preferences(
        transpilation_option=TranspilationOption.INTENSIVE,
        custom_hardware_settings=CustomHardwareSettings(basis_gates=["u3", "cx"]),
    ),
)

raw_submission_qasm = export(
    transpiled, TargetLanguage.QASM2,
    transpilation_config=TranspilationConfig(transpilation_level=TranspilationOption.INTENSIVE, basis_gates=["u3", "cx"]),
)

tk_circ = circuit_from_qasm_str(raw_submission_qasm)
FullPeepholeOptimise().apply(tk_circ)
AutoRebase({OpType.U3, OpType.CX}).apply(tk_circ)

print("="*40)
print(f"TRIE-BASED ESOP SYNTHESIS METRICS:")
print(f"Depth    = {tk_circ.depth()}")
print(f"CX count = {tk_circ.n_gates_of_type(OpType.CX)}")
print(f"Width    = {tk_circ.n_qubits}")
print("="*40)

final_qasm = circuit_to_qasm_str(tk_circ)
with open("submission.qasm", "w") as f:
    f.write(final_qasm)
with open("submission_package/submission.qasm", "w") as f:
    f.write(final_qasm)

print("Saved submission.qasm successfully.")
