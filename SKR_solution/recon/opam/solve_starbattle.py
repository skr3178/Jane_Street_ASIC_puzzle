#!/usr/bin/env python3
# Independent Star Battle solver over the region map recovered from the chip; enumerates ALL solutions.
import itertools, sys
REG = """DDDDDJJABBI
DDFDDJAABBI
DDFJJJJAABI
DDFJEEEIAAI
FDFJEIIIIII
FFFJEEEIHHH
JJJJJJEIHKK
JCCCEEEIHKK
JCCGIIIIHKK
JJCGGIIIHHH
JCCGIIIIIII""".split()
N=11; K=2
reg=[[ord(ch)-65 for ch in row] for row in REG]
NR=max(max(r) for r in reg)+1
rowopts=[]
for cs in itertools.combinations(range(N),K):
    if all(b-a>1 for a,b in zip(cs,cs[1:])): rowopts.append(cs)
sols=[]
colcnt=[0]*N; regcnt=[0]*NR
def rec(r, prev, placed):
    if r==N:
        sols.append([tuple(p) for p in placed]); return
    for cs in rowopts:
        if any(abs(c-p)<=1 for c in cs for p in prev): continue
        from collections import Counter
        rc=Counter(reg[r][c] for c in cs)
        if any(colcnt[c]>=K for c in cs) or any(regcnt[g]+k>K for g,k in rc.items()): continue
        # remaining-capacity pruning: every column/region must still be able to reach K
        for c in cs: colcnt[c]+=1; regcnt[reg[r][c]]+=1
        rows_left=N-r-1
        if all(colcnt[c]+rows_left>=K for c in range(N)):
            placed.append(cs); rec(r+1, cs, placed); placed.pop()
        for c in cs: colcnt[c]-=1; regcnt[reg[r][c]]-=1
rec(0, (), [])
print("number of solutions:", len(sols))
KEY=open("recon/opam/key.mem").read().split()[0]
for s in sols:
    bits="".join("1" if c in s[r] else "0" for r in range(N) for c in range(N))
    print(" solution == key[0:121]:", bits==KEY[:121])
    for r in range(N): print("   "+" ".join("*" if c in s[r] else "." for c in range(N)))
