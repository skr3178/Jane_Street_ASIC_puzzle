#!/usr/bin/env python3
# (1) exact ANF of the O[7:0] output cone  (2) read the 57-bit accept target
import sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hash", "anf"))
sys.argv = ["x"]                       # anf_extract runs its main at import; harmless
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import netparse as A

def fmt(f):
    if not f: return "0"
    terms = (["1"] if frozenset() in f else []) + \
            sorted(("&".join(sorted(m)) for m in f if m), key=lambda s:(s.count("&"),s))
    return " ^ ".join(terms)

print("== O output cone (exact ANF over flop Q's / PIs) ==")
for i in range(8):
    net = f"O[{i}]"
    sup = sorted(A.support(net))
    f = A.anf(net)
    print(f"O[{i}]  support={len(sup)} deg={max(len(m) for m in f)} #mon={len(f)}")
    print("      = " + fmt(f))
print("success =", fmt(A.anf("success")))
