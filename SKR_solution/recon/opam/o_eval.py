# Boolean evaluator of the O cone directly from the netlist (fast, no ANF)
import sys, io, contextlib, itertools, pickle, os
sys.path.insert(0, "recon/opam")
with contextlib.redirect_stdout(io.StringIO()):
    import netparse as A
def ev(node, env):
    op = node[0]
    if op == "var": return env[node[1]]
    if op == "not": return 1 - ev(node[1], env)
    a, b = ev(node[1], env), ev(node[2], env)
    return {"and": a & b, "or": a | b, "xor": a ^ b}[op]
def val(net, st, memo):
    if net in memo: return memo[net]
    if net in A.const_nets: r = 1 if A.const_nets[net] else 0
    elif net in A.statevar: r = st[A.statevar[net]]
    elif net in A.PIS: r = st[net]
    else:
        ctype, iname, opin, pins = A.drivers[net]
        env = {p: val(n, st, memo) for p, n in pins.items() if p != opin}
        r = ev(A.funcast[(ctype, opin)], env)
    memo[net] = r; return r
SUP = sorted(set().union(*[A.support(f"O[{i}]") for i in range(8)]), key=lambda x:int(x.split("__")[1]))
print("union support", len(SUP), SUP)
def O(st):
    memo = {}
    return sum(val(f"O[{i}]", st, memo) << i for i in range(8))
if __name__ == "__main__":
    # full truth table over the 23-var union support is 8M rows -- too many; instead probe structure.
    base = {v: 0 for v in SUP}
    import random
    # 1) does O depend on anything when g__243=0 ?
    r = random.Random(1)
    for g243 in (0,1):
        outs=set()
        for _ in range(2000):
            st = {v: r.randint(0,1) for v in SUP}; st["g__243"]=g243
            outs.add(O(st))
        print(f"g__243={g243}: distinct O values in 2000 random states: {len(outs)}", sorted(outs)[:10])
