# Count 11x11 boards with exactly 2 stars per row and column and no touching stars (regions ignored).
import itertools
N=11
rowopts=[cs for cs in itertools.combinations(range(N),2) if cs[1]-cs[0]>1]
compat={a:[b for b in rowopts if all(abs(x-y)>1 for x in a for y in b)] for a in rowopts}
def enc(cnt): 
    v=0
    for c in cnt: v=v*3+c
    return v
# DP state: (colcount tuple, prev row) -> ways
from collections import defaultdict
states=defaultdict(int)
for cs in rowopts:
    cnt=[0]*N
    for c in cs: cnt[c]=1
    states[(tuple(cnt),cs)]+=1
for r in range(1,N):
    nxt=defaultdict(int); left=N-r-1
    for (cnt,prev),w in states.items():
        for cs in compat[prev]:
            if cnt[cs[0]]>=2 or cnt[cs[1]]>=2: continue
            c2=list(cnt); c2[cs[0]]+=1; c2[cs[1]]+=1
            if any(c2[i]+left<2 for i in range(N)): continue
            nxt[(tuple(c2),cs)]+=w
    states=nxt
    print("row",r,"states",len(states),flush=True)
print("TOTAL boards (rows=cols=2, no touching, regions ignored):", sum(states.values()))
