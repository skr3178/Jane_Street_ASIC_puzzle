#!/usr/bin/env python3
# Exact ANF (XOR-of-ANDs over GF(2)) of every flop's next-state function,
# extracted from the netlist + sky130 Liberty cell functions.
import re, json, sys, os
from collections import defaultdict

HERE     = os.path.dirname(os.path.abspath(__file__))
NETLIST  = os.path.join(HERE, "..", "..", "hash", "extracted_puzzle.v")
LIB      = os.path.expanduser("~/.ciel/ciel/sky130/versions/"
           "8afc8346a57fe1ab7934ba5a6056ea8b43078e71/sky130A/libs.ref/"
           "sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib")
META     = os.path.join(HERE, "..", "..", "hash", "linearity", "flop_meta.json")
CAP      = 1_000_000          # monomial blowup guard (wide comparators explode)
SEQ      = {"dfrtp_2", "dfstp_2", "dfxtp_2"}
PIS      = {"I", "clk", "enable", "rst_n"}

class Blowup(Exception): pass

# ---------- ANF algebra: function = set of frozenset(varnames) ----------
ONE, ZERO = {frozenset()}, set()
def XOR(a, b): return a ^ b
def NOT(a):    return a ^ ONE
def AND(a, b):
    out = set()
    for m1 in a:
        for m2 in b:
            m = m1 | m2
            if m in out: out.discard(m)
            else:        out.add(m)
    if len(out) > CAP: raise Blowup()
    return out
def OR(a, b):  return XOR(XOR(a, b), AND(a, b))

# ---------- Liberty: cell -> {output_pin: expr_string} ----------
libtext = open(LIB).read()
def cell_block(name):
    i = libtext.find(f'cell ("{name}")')
    if i < 0: raise KeyError(name)
    j = libtext.index("{", i); depth, k = 1, j + 1
    while depth:
        depth += {"{": 1, "}": -1}.get(libtext[k], 0); k += 1
    return libtext[j:k]
def cell_funcs(name):
    blk, funcs = cell_block(name), {}
    for m in re.finditer(r'pin\s*\(\s*"?(\w+)"?\s*\)\s*{', blk):
        j = m.end() - 1; depth, k = 1, j + 1
        while depth:
            depth += {"{": 1, "}": -1}.get(blk[k], 0); k += 1
        f = re.search(r'(?<![\w_])function\s*:\s*"([^"]+)"', blk[j:k])
        if f: funcs[m.group(1)] = f.group(1)
    return funcs

# ---------- Liberty boolean-expression parser -> AST ----------
def tokenize(s): return re.findall(r"[A-Za-z_][A-Za-z0-9_]*|[!&|^()'+*]", s)
def parse(tokens):
    pos = [0]
    def peek(): return tokens[pos[0]] if pos[0] < len(tokens) else None
    def eat():  pos[0] += 1; return tokens[pos[0] - 1]
    def atom():
        t = eat()
        node = parse_or() if t == "(" else ("var", t)
        if t == "(": assert eat() == ")"
        while peek() == "'": eat(); node = ("not", node)
        return node
    def unary():
        if peek() == "!": eat(); return ("not", unary())
        return atom()
    def parse_and():
        n = unary()
        while peek() in ("&", "*"): eat(); n = ("and", n, unary())
        return n
    def parse_xor():
        n = parse_and()
        while peek() == "^": eat(); n = ("xor", n, parse_and())
        return n
    def parse_or():
        n = parse_xor()
        while peek() in ("|", "+"): eat(); n = ("or", n, parse_xor())
        return n
    return parse_or()
def eval_ast(node, env):
    op = node[0]
    if op == "var": return env[node[1]]
    if op == "not": return NOT(eval_ast(node[1], env))
    a, b = eval_ast(node[1], env), eval_ast(node[2], env)
    return {"and": AND, "or": OR, "xor": XOR}[op](a, b)

# ---------- Parse netlist ----------
def clean(n):
    n = n.strip()
    return n[1:].strip() if n.startswith("\\") else n
insts = []
for m in re.finditer(r"sky130_fd_sc_hd__(\w+)\s+(\S+)\s+\((.*?)\);",
                     open(NETLIST).read(), re.S):
    ctype, iname, body = m.groups()
    pins = {p: clean(n) for p, n in re.findall(r"\.(\w+)\(([^)]*)\)", body)}
    insts.append((ctype, iname, pins))

const_nets, statevar, drivers, flops = {}, {}, {}, {}
funcast = {}                                  # (ctype, outpin) -> AST
for ctype, iname, pins in insts:
    if ctype == "conb_1":
        if "HI" in pins: const_nets[pins["HI"]] = ONE
        if "LO" in pins: const_nets[pins["LO"]] = ZERO
    elif ctype in SEQ:
        statevar[pins["Q"]] = iname           # Q net becomes a variable
        flops[iname] = (ctype, pins)
    else:
        if not any(k[0] == ctype for k in funcast):
            for opin, expr in cell_funcs(f"sky130_fd_sc_hd__{ctype}").items():
                funcast[(ctype, opin)] = parse(tokenize(expr))
        for p, net in pins.items():
            if (ctype, p) in funcast:
                drivers[net] = (ctype, iname, p, pins)

# ---------- Evaluate cones (memoized) ----------
sys.setrecursionlimit(1000000)
memo = {}
def anf(net):
    if net in memo:        return memo[net]
    if net in const_nets:  r = const_nets[net]
    elif net in statevar:  r = {frozenset([statevar[net]])}
    elif net in PIS:       r = {frozenset([net])}
    elif net in drivers:
        ctype, iname, opin, pins = drivers[net]
        env = {p: anf(n) for p, n in pins.items() if p != opin}
        r = eval_ast(funcast[(ctype, opin)], env)
    else:
        print(f"  [warn] undriven net {net} -> free variable"); r = {frozenset(["U_" + net])}
    memo[net] = r
    return r
def support(net, seen=None):                  # structural support, blowup-proof
    seen = seen if seen is not None else set()
    if net in seen: return set()
    seen.add(net)
    if net in const_nets: return set()
    if net in statevar:   return {statevar[net]}
    if net in PIS:        return {net}
    if net in drivers:
        _, _, opin, pins = drivers[net]
        subs = [support(n, seen) for p, n in pins.items() if p != opin]
        return set().union(*subs) if subs else set()
    return {"U_" + net}

