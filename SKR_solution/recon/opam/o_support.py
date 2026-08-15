import sys, os, io, contextlib
sys.path.insert(0, "recon/opam")
with contextlib.redirect_stdout(io.StringIO()):
    import anf_extract as A
for i in range(8):
    s = sorted(A.support(f"O[{i}]"), key=lambda x:(x[0], int(x.split("__")[1]) if "__" in x else 0))
    print(f"O[{i}] support={len(s)}:", " ".join(s))
# how many cells in each cone
def cone(net, seen):
    if net in seen or net in A.const_nets or net in A.statevar or net in A.PIS: return
    seen.add(net)
    if net in A.drivers:
        _, iname, opin, pins = A.drivers[net]
        for p, n in pins.items():
            if p != opin: cone(n, seen)
allc=set()
for i in range(8):
    c=set(); cone(f"O[{i}]", c); print(f"O[{i}] cone nets: {len(c)}"); allc|=c
print("union cone nets:", len(allc))
