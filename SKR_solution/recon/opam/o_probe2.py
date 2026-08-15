import sys, random, itertools
sys.path.insert(0, "recon/opam")
from o_eval import *
r = random.Random(2)
CTRL = ["g__197","g__248","g__9","g__10","g__11","g__539"]
DATA = [v for v in SUP if v not in CTRL and v!="g__243"]
# For each control combo, find which data vars O bits depend on (by flipping) 
for combo in itertools.product((0,1), repeat=len(CTRL)):
    dep = {i:set() for i in range(8)}
    consts = [set() for _ in range(8)]
    for _ in range(60):
        st = {v: r.randint(0,1) for v in SUP}; st["g__243"]=1
        st.update(dict(zip(CTRL, combo)))
        o = O(st)
        for i in range(8): consts[i].add((o>>i)&1)
        for v in DATA:
            st2 = dict(st); st2[v]^=1; o2 = O(st2)
            for i in range(8):
                if ((o^o2)>>i)&1: dep[i].add(v)
    desc = []
    for i in range(8):
        if not dep[i]: desc.append(f"O{i}={consts[i].pop()}")
        else: desc.append(f"O{i}<-{','.join(sorted(dep[i], key=lambda x:int(x[3:])))}")
    print(dict(zip(CTRL,combo)), " | ".join(desc))
