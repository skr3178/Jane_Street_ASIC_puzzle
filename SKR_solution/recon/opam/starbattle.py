#!/usr/bin/env python3
# Hypothesis: the chip verifies an 11x11 two-star Star Battle. Check the key + build the region map from the automata.
import re, itertools, sys
sys.argv=[""]
exec(open("recon/opam/automata.py").read().split("summary=[]")[0])   # reuse eq/ev/traj/pairs/KEY
N=11
grid=[[int(KEY[r*N+c]) for c in range(N)] for r in range(N)]
print("key bit 121 (beyond the grid) =", KEY[121], "  popcount(0..120) =", sum(map(int,KEY[:121])))
print("\nGrid (row-major, * = 1):")
for r in range(N): print("  "+" ".join("*" if grid[r][c] else "." for c in range(N)))
print("\nrow sums   :", [sum(grid[r]) for r in range(N)])
print("column sums:", [sum(grid[r][c] for r in range(N)) for c in range(N)])
adj=0
for r in range(N):
    for c in range(N):
        if grid[r][c]:
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if (dr or dc) and 0<=r+dr<N and 0<=c+dc<N and grid[r+dr][c+dc]: adj+=1
print("touching star pairs (incl. diagonal):", adj//2)
# region map from the 11 non-column automata
region=[[None]*N for _ in range(N)]
label=0
for a,b in pairs:
    A,B=f"g__{a}",f"g__{b}"
    watch=[]
    for p in range(122):
        base=dict(traj[p]); base["enable"]=1
        for sa,sb,I in itertools.product((0,1),(0,1),(0,1)):
            s=dict(base); s[A]=sa; s[B]=sb; s["I"]=I
            if (ev(A,s),ev(B,s))!=(sa,sb): watch.append(p); break
    if len(watch)==11 and len(set(p%11 for p in watch))==1: continue   # a column
    label+=1
    for p in watch: region[p//N][p%N]=label
print("\nRegion map (from the 11 non-column automata):")
L="ABCDEFGHIJK"
for r in range(N): print("  "+" ".join(L[region[r][c]-1] if region[r][c] else "?" for c in range(N)))
print("region sizes:", {L[i]: sum(row.count(i+1) for row in region) for i in range(label)})
print("stars per region:", {L[i]: sum(grid[r][c] for r in range(N) for c in range(N) if region[r][c]==i+1) for i in range(label)})
print("\nGrid with regions (uppercase = star):")
for r in range(N): print("  "+" ".join((L[region[r][c]-1] if grid[r][c] else L[region[r][c]-1].lower()) for c in range(N)))
