#!/usr/bin/env python3
# Enumerate the 22 accept-check pair-automata: which input positions each one watches, and its transition rules.
import re, itertools
eq = {}
for l in open("hash/anf/anf_equations.txt"):
    m = re.match(r"(g__\d+)' = (.*)", l.strip())
    if m and not m.group(2).startswith("["):
        eq[m.group(1)] = [frozenset(t.split("&")) for t in m.group(2).split(" ^ ")]
def ev(v, st):
    r = 0
    for mon in eq[v]:
        if all(st.get(x, 0) for x in mon): r ^= 1
    return r
CTRL = ["g__199","g__237","g__221","g__245","g__187","g__181","g__250","g__251","g__180"]
# counter trajectory: reset -> 3 cycles rst (all 0) -> cycle3 enable=0 -> cycles 4.. enable=1
st = {c:0 for c in CTRL}; st["g__243"]=0
traj = []   # counter state at the START of each enable cycle (position p = cycle-4)
st["enable"]=0; nxt={c:ev(c,st) for c in CTRL}; nxt["g__243"]=ev("g__243",st); st=nxt   # cycle 3 (enable=0)
for p in range(130):
    traj.append(dict(st))
    st["enable"]=1; nxt={c:ev(c,st) for c in CTRL}; nxt["g__243"]=ev("g__243",st); st=nxt
# sanity: g__180 rises when?
print("g__180 first 1 at position", next(p for p,s in enumerate(traj) if s["g__180"]), "(cycle", 4+next(p for p,s in enumerate(traj) if s["g__180"]),")")
pairs = [(261,198),(262,219),(204,260),(188,228),(207,184),(238,202),(200,242),(226,253),(218,217),(214,179),(263,216),
         (244,222),(249,211),(234,203),(189,210),(213,230),(257,194),(252,192),(195,182),(232,241),(229,193),(235,225)]
KEY = open("recon/opam/key.mem").read().split()[0]
summary=[]
for a,b in pairs:
    A,B=f"g__{a}",f"g__{b}"
    watch = {}   # position -> transition table {(sa,sb,I):(sa',sb')} restricted to non-trivial
    for p in range(122):
        base = dict(traj[p]); base["enable"]=1
        tt = {}
        for sa,sb,I in itertools.product((0,1),(0,1),(0,1)):
            s = dict(base); s[A]=sa; s[B]=sb; s["I"]=I
            n = (ev(A,s), ev(B,s))
            if n != (sa,sb): tt[(sa,sb,I)] = n
        if tt: watch[p]=tt
    # run on key
    sa=sb=0; path=[]
    for p in range(122):
        s=dict(traj[p]); s["enable"]=1; s[A]=sa; s[B]=sb; s["I"]=int(KEY[p])
        sa,sb = ev(A,s), ev(B,s)
        if p in watch: path.append((p,int(KEY[p]),(sa,sb)))
    # collapse: rules that are identical across positions
    rules = {}
    for p,tt in watch.items(): rules.setdefault(tuple(sorted(tt.items())), []).append(p)
    summary.append((A,B,watch,rules,(sa,sb),path))
    print(f"\n== pair (a={A}, b={B}) watches {len(watch)} positions: {sorted(watch)}")
    for tt,ps in rules.items():
        print(f"   at positions {ps}:")
        for (s0a,s0b,I),(n0a,n0b) in tt: print(f"      state ({s0a},{s0b}), I={I} -> ({n0a},{n0b})")
    print(f"   key path: {path}  final={(sa,sb)}  (need (0,1))")
