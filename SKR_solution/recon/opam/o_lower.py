# Emit the O[7:0] output cone as readable Verilog assigns (topological), from netlist + Liberty
import sys, re
sys.path.insert(0, "recon/opam")
import netparse as A
def vname(net):
    if net in A.statevar: return A.statevar[net]
    if net in A.PIS: return net
    m = re.fullmatch(r"O\[(\d)\]", net)
    if m: return f"o_{m.group(1)}"
    return "n_" + re.sub(r"[^A-Za-z0-9_]", "_", net).strip("_")
def expr(node, pins):
    op = node[0]
    if op == "var": return vname(pins[node[1]])
    if op == "not": return "~" + expr(node[1], pins)
    sym = {"and": "&", "or": "|", "xor": "^"}[op]
    return "(" + expr(node[1], pins) + " " + sym + " " + expr(node[2], pins) + ")"
order, seen = [], set()
def walk(net):
    if net in seen or net in A.const_nets or net in A.statevar or net in A.PIS: return
    seen.add(net)
    ctype, iname, opin, pins = A.drivers[net]
    for p, n in pins.items():
        if p != opin: walk(n)
    order.append(net)
for i in range(8): walk(f"O[{i}]")
lines = []
for net in order:
    ctype, iname, opin, pins = A.drivers[net]
    e = expr(A.funcast[(ctype, opin)], pins)
    for cn in A.const_nets:                     # inline constants
        e = e.replace(vname(cn), "1'b1" if A.const_nets[cn] else "1'b0")
    lines.append(f"  wire {vname(net)} = {e};   // {iname} {ctype}")
print(f"// {len(order)} cells in the O cone")
print("\n".join(lines))
print("  assign O = { o_7, o_6, o_5, o_4, o_3, o_2, o_1, o_0 };")
