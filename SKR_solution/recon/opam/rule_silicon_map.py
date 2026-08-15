# Colour every std cell of the real placement by the Star Battle rule it implements.
import json, sys, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0,"recon/opam"); import netparse as A
place={n:(c,x,y) for n,c,x,y in json.load(open("recon/opam/placement.json"))}
g=lambda *ns:[f"g__{n}" for n in ns]
CLASS={}
def tag(names,cls):
    for n in names: CLASS[n]=cls
tag(g(199,237,221,245,187,181,250,251,180,243),"position counter / done")
cols=[(244,222),(249,211),(234,203),(189,210),(213,230),(257,194),(252,192),(195,182),(232,241),(229,193),(235,225)]
regs=[(261,198),(262,219),(204,260),(188,228),(207,184),(238,202),(200,242),(226,253),(218,217),(214,179),(263,216)]
tag(g(*[x for p in cols for x in p]),"column counters (11×2 flops)")
tag(g(*[x for p in regs for x in p]),"region counters (11×2 flops)")
tag(g(258,259,254),"row check")
tag(g(186,209,247,220,196,223,178,212,185,255,240,231,205),"no-touch check (delay line + flag)")
tag(g(183,190,233,236,393,224,215,201),"popcount")
tag(g(197,248),"success latches")
tag(g(9,10,11,539,12,13,14,206,208,227,256,405),"output generator")
assert len(CLASS)==92, len(CLASS)
# assign combinational cells: walk each flop's D cone; a cell feeding cones of one class gets that class
cell_cls={}
def cone(net,acc,seen):
    if net in seen or net in A.const_nets or net in A.statevar or net in A.PIS: return
    seen.add(net); ctype,iname,opin,pins=A.drivers[net]; acc.add(iname)
    for p,n in pins.items():
        if p!=opin: cone(n,acc,seen)
from collections import defaultdict
votes=defaultdict(set)
for iname,(ctype,pins) in A.flops.items():
    acc=set(); cone(pins["D"],acc,set())
    for c in acc: votes[c].add(CLASS[iname])
for i in range(8):
    acc=set(); cone(f"O[{i}]",acc,set())
    for c in acc: votes[c].add("output generator")
for c,v in votes.items(): cell_cls[c]=next(iter(v)) if len(v)==1 else "shared logic"
for f in A.flops: cell_cls[f]=CLASS[f]
COL={"position counter / done":"#d62728","column counters (11×2 flops)":"#1f77b4","region counters (11×2 flops)":"#17becf",
     "row check":"#ff7f0e","no-touch check (delay line + flag)":"#2ca02c","popcount":"#8c564b","success latches":"#e377c2",
     "output generator":"#9467bd","shared logic":"#bbbbbb"}
fig,ax=plt.subplots(figsize=(7.5,10))
for cls,col in COL.items():
    fl=[(x,y) for n,(c,x,y) in place.items() if cell_cls.get(n)==cls and n in A.flops]
    cb=[(x,y) for n,(c,x,y) in place.items() if cell_cls.get(n)==cls and n not in A.flops]
    if cb: ax.scatter(*zip(*cb),s=14,color=col,alpha=0.55,marker='s',lw=0)
    if fl: ax.scatter(*zip(*fl),s=46,color=col,edgecolor='k',lw=0.5,marker='o',label=f"{cls}  ({len(fl)} flops, {len(cb)} gates)")
un=[(x,y) for n,(c,x,y) in place.items() if n not in cell_cls]
if un: ax.scatter(*zip(*un),s=8,color="#dddddd",marker='s',lw=0,label=f"unclassified ({len(un)})")
ax.set_aspect('equal'); ax.set_xlabel("x (µm)"); ax.set_ylabel("y (µm)"); ax.grid(alpha=0.25)
ax.set_title("Star Battle rules mapped onto the real placement (puzzle.gds)\nflops = circles, gates = squares, coloured by the rule they implement",fontsize=11)
ax.legend(fontsize=7.5,loc='upper center',bbox_to_anchor=(0.5,-0.07),ncol=2,frameon=False)
plt.tight_layout(); plt.savefig("recon/opam/rule_silicon_map.png",dpi=150)
print({k:sum(1 for v in cell_cls.values() if v==k) for k in COL})
