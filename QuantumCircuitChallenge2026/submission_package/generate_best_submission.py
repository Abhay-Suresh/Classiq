import json
import numpy as np
from collections import Counter
import classiq
from classiq import *
from classiq.qmod.symbolic import pi
from classiq.interface.generator.hardware.hardware_data import CustomHardwareSettings
from classiq import Constraints, OptimizationParameter, Preferences, TranspilationConfig, TranspilationOption
from pytket.qasm import circuit_from_qasm_str, circuit_to_qasm_str
from pytket.passes import FullPeepholeOptimise, AutoRebase, OptimisePhaseGadgets, SynthesiseTket, RemoveRedundancies
from pytket.circuit import OpType

from pathlib import Path

# Load the 60-cube champion ESOP
pkg_dir = Path(__file__).parent
with open(pkg_dir / "optimized_esop_60.json") as f:
    esop = json.load(f)

all_cubes = []
for ym, yv, xm, xv in esop:
    lits = set()
    for i in range(6):
        if (ym >> i) & 1: lits.add(('y', i, (yv >> i) & 1))
        if (xm >> i) & 1: lits.add(('x', i, (xv >> i) & 1))
    all_cubes.append(frozenset(lits))

class TrieNode:
    def __init__(self, lit=None):
        self.lit = lit
        self.is_terminal = False
        self.children = []
        self.leaf_cubes = []

def build_advanced_trie(cubes, min_freq=2, score_mode='freq', var_priority=None):
    if not cubes: return None
    has_empty = frozenset() in cubes
    non_empty = [c for c in cubes if c != frozenset()]
    node = TrieNode()
    if has_empty: node.is_terminal = True
    if not non_empty: return node

    counts = Counter()
    for c in non_empty:
        for lit in c: counts[lit] += 1

    def get_score(lit):
        c = counts[lit]
        var, idx, val = lit
        score = float(c)
        if score_mode == 'len_weighted':
            avg_len = np.mean([len(cube) for cube in non_empty if lit in cube])
            score *= avg_len
        elif score_mode == 'prod':
            score = (c ** 1.5)
        if var_priority and var == var_priority:
            score *= 2.0
        return score

    all_lits = list(counts.keys())
    all_lits.sort(key=get_score, reverse=True)
    best_lit = all_lits[0]
    max_c = counts[best_lit]

    if max_c < min_freq:
        node.leaf_cubes = non_empty
        return node

    with_lit = []
    without_lit = []
    for c in non_empty:
        if best_lit in c: with_lit.append(c - {best_lit})
        else: without_lit.append(c)

    child_node = build_advanced_trie(with_lit, min_freq, score_mode, var_priority)
    child_node.lit = best_lit
    node.children.append(child_node)

    if without_lit:
        other_child = build_advanced_trie(without_lit, min_freq, score_mode, var_priority)
        node.children.append(other_child)
    return node

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
            cond = (reg[idx] == val)
            control(cond, lambda: render_node(child, x, y))
        else:
            render_node(child, x, y)

trie_root = build_advanced_trie(all_cubes, min_freq=2, score_mode='freq', var_priority=None)

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
candidate_qasm = "\n".join(line for line in raw_lines
                           if not (line.lstrip().startswith("hadamard_transform_") and "q[" in line))

transpiled = classiq.transpile(
    quantum_program_from_qasm(candidate_qasm),
    preferences=Preferences(
        transpilation_option=TranspilationOption.INTENSIVE,
        custom_hardware_settings=CustomHardwareSettings(basis_gates=["u3", "cx"]),
    ),
)
raw_sub = export(transpiled, TargetLanguage.QASM2,
                 transpilation_config=TranspilationConfig(transpilation_level=TranspilationOption.INTENSIVE, basis_gates=["u3", "cx"]))

tk_circ = circuit_from_qasm_str(raw_sub)
for i in range(5):
    old_depth = tk_circ.depth()
    SynthesiseTket().apply(tk_circ)
    FullPeepholeOptimise().apply(tk_circ)
    AutoRebase({OpType.U3, OpType.CX}).apply(tk_circ)
    RemoveRedundancies().apply(tk_circ)
    if tk_circ.depth() == old_depth:
        break

print("="*40)
print(f"NEW METRICS:")
print(f"Depth    = {tk_circ.depth()}")
print(f"CX count = {tk_circ.n_gates_of_type(OpType.CX)}")
print(f"Width    = {tk_circ.n_qubits}")
print("="*40)

final_qasm = circuit_to_qasm_str(tk_circ)
with open(pkg_dir / "submission.qasm", "w") as f:
    f.write(final_qasm)
with open(pkg_dir.parent / "submission.qasm", "w") as f:
    f.write(final_qasm)

print("Saved submission.qasm successfully.")
