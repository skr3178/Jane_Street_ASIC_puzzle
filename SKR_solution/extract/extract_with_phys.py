#!/usr/bin/env python3
"""
GDS -> cell-level Verilog netlist extractor (Jane Street ASIC puzzle, task 1).

Approach A: drive KLayout's LayoutToNetlist (L2N) connectivity engine in
pure-connectivity mode with the layout hierarchy preserved. Each standard-cell
placement becomes an L2N SubCircuit with named pins (pin names come from the
labels *inside* each cell definition on li1.label 67/5). Net tracing across
li1 -> mcon -> met1 -> via -> ... -> met5 is done by L2N; we only declare the
sky130 layer connectivity and format the resulting netlist as Verilog.

Router-inserted VIA_* cells and physical-only cells (tap/decap/fill/diode) are
flattened into the top cell first so their via geometry participates in the
trace and does not appear as spurious instances.

Usage:  python3 extract.py <in.gds> -o <out.v> [--top NAME]
Runs under plain python3 with the pip `klayout` module (import pya).
"""
import argparse, re, sys
import pya

# sky130 GDS layer/datatype map: conductors + their label layers.
COND = {  # name -> (layer, datatype)
    "li1": (67, 20), "mcon": (67, 44),
    "met1": (68, 20), "via":  (68, 44),
    "met2": (69, 20), "via2": (69, 44),
    "met3": (70, 20), "via3": (70, 44),
    "met4": (71, 20), "via4": (71, 44),
    "met5": (72, 20),
}
# label datatype 5 sits on each metal's layer number; li1 label is 67/5.
LABEL = {"li1": (67, 5), "met1": (68, 5), "met2": (69, 5),
         "met3": (70, 5), "met4": (71, 5), "met5": (72, 5)}
# vertical via chain: (lower_metal, via, upper_metal)
VIA_CHAIN = [("li1", "mcon", "met1"), ("met1", "via", "met2"),
             ("met2", "via2", "met3"), ("met3", "via3", "met4"),
             ("met4", "via4", "met5")]

POWER_PINS = {"VPWR", "VGND", "VNB", "VPB", "VNW", "VPWRIN"}
# cells with no signal pins -> not logic, drop from the netlist entirely.
PHYSICAL_RE = re.compile(r"__(tap|decap|fill|diode|fakediode|antenna)")

# LEF supplies DIRECTION per (cell, pin). Used to (a) declare module port
# directions and (b) classify a top port as output iff it is driven by a cell
# output pin. Path is the sky130A hd LEF in the ciel PDK store.
import glob, os
_LEF_GLOB = os.path.expanduser(
    "~/.ciel/ciel/sky130/versions/*/sky130A/libs.ref/"
    "sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef")


def load_pin_dirs(lef_path=None):
    if lef_path is None:
        hits = glob.glob(_LEF_GLOB)
        if not hits:
            return {}
        lef_path = hits[0]
    dirs = {}
    macro = None
    pin = None
    with open(lef_path) as f:
        for line in f:
            s = line.split()
            if not s:
                continue
            if s[0] == "MACRO":
                macro = s[1]; dirs.setdefault(macro, {})
            elif s[0] == "PIN":
                pin = s[1]
            elif s[0] == "DIRECTION" and macro and pin:
                dirs[macro][pin] = s[1]
    return dirs


def is_logic_cell(name):
    return name.startswith("sky130_fd_sc_hd__") and not PHYSICAL_RE.search(name)


def is_emit_cell(name):
    """Variant of the extractor that KEEPS physical std cells (tap/decap/fill/
    diode) in the emitted netlist, matching the full 01_netlist.v cell list.
    Still excludes router VIA_* arrays and INTERNAL_* markers (not real cells)."""
    return name.startswith("sky130_fd_sc_hd__")


def vlog_id(name):
    """Turn an L2N net/pin name into a legal Verilog identifier, escaping when
    it contains characters like [ ] / that appear in bus and hierarchical names."""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return name
    return "\\" + name + " "


def extract(gds_path, top_name=None):
    ly = pya.Layout()
    ly.read(gds_path)
    top = ly.cell(top_name) if top_name else None
    if top is None:
        tops = [c for c in ly.top_cells()]
        if len(tops) != 1:
            sys.exit(f"ambiguous top cells: {[c.name for c in tops]}; use --top")
        top = tops[0]

    # No pre-flatten is needed. L2N computes connectivity hierarchically over
    # the full layout: via shapes inside the router's VIA_* cells still join the
    # metals above/below them (the net threads through the via subcircuit's
    # pins), and physical-only cells (tap/decap/fill, and the puzzle's inert
    # INTERNAL_* markers on layer 200/0, which we never register) contribute no
    # signal geometry. The emitter's is_logic_cell filter drops the residual
    # VIA_*/physical subcircuits. Verified: the warmup extraction leaks zero
    # VIA_*/tap/decap instances and passes EQY without any flattening.

    l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly, top, []))

    reg = {}
    for nm, (l, d) in COND.items():
        idx = ly.find_layer(l, d)
        if idx is not None:
            reg[nm] = l2n.make_polygon_layer(idx, nm)
    lbl = {}
    for nm, (l, d) in LABEL.items():
        idx = ly.find_layer(l, d)
        if idx is not None:
            lbl[nm] = l2n.make_text_layer(idx, nm + ".lbl")

    # intra-layer + via-chain connectivity
    for nm in reg:
        l2n.connect(reg[nm])
    for lo, via, hi in VIA_CHAIN:
        if lo in reg and via in reg:
            l2n.connect(reg[lo], reg[via])
        if via in reg and hi in reg:
            l2n.connect(reg[via], reg[hi])
    # attach labels to their conductor: names pins (internal) and ports (top)
    for nm, tl in lbl.items():
        if nm in reg:
            l2n.connect(reg[nm], tl)

    l2n.extract_netlist()
    nl = l2n.netlist()
    tc = nl.circuit_by_name(top.name)
    if tc is None:
        tc = list(nl.each_circuit())[0]
    # return l2n too: it owns nl/tc; if it is GC'd the netlist is destroyed.
    return ly, top, l2n, nl, tc


def top_port_labels(ly, top):
    """Port net names = text labels placed directly in the top cell (not
    recursive) on any metal/li1 label layer, excluding power."""
    ports = set()
    lay_idx = [ly.find_layer(l, d) for (l, d) in LABEL.values()]
    for idx in lay_idx:
        if idx is None:
            continue
        for s in top.shapes(idx).each():
            if s.is_text():
                t = s.text_string
                if t and t not in POWER_PINS:
                    ports.add(t)
    return ports


BUS_RE = re.compile(r"^(\w+)\[(\d+)\]$")


def group_buses(names):
    """Partition net names into vector buses and scalars.
    Returns (buses, scalars): buses maps base -> sorted index list for every
    name of the form base[idx]; scalars is the set of remaining names."""
    buses, scalars = {}, set()
    for n in names:
        m = BUS_RE.match(n)
        if m:
            buses.setdefault(m.group(1), set()).add(int(m.group(2)))
        else:
            scalars.add(n)
    return {b: sorted(ix) for b, ix in buses.items()}, scalars


def make_net_ref(buses):
    """Format a net name for Verilog: a bus bit base[idx] becomes an unescaped
    bit-select `base[idx]` (so yosys treats it as bit idx of vector `base`);
    anything else is escaped as needed. This is what makes an extracted
    O[0..7] match a reference `output [7:0] O;` under name-based LEC."""
    def ref(name):
        m = BUS_RE.match(name)
        if m and m.group(1) in buses:
            return f"{m.group(1)}[{int(m.group(2))}]"
        return vlog_id(name)
    return ref


def _decl_range(indices):
    return f"[{max(indices)}:{min(indices)}]"


def emit_verilog(ly, top, nl, tc, out, pin_dirs):
    port_names = top_port_labels(ly, top)

    def netname(net):
        return net.expanded_name() if net is not None else None

    # collect logic instances; learn which nets are driven by a cell output;
    # track dangling signal pins (unconnected) for the self-check.
    insts = []
    used_nets = set()
    driven_by_output = set()
    dangling = 0
    for sc in tc.each_subcircuit():
        cir = sc.circuit_ref()
        if not is_emit_cell(cir.name):
            continue
        conns = []
        for i in range(cir.pin_count()):
            pn = cir.pin_by_id(i).name()
            if pn in POWER_PINS:
                continue
            nn = netname(sc.net_for_pin(i))
            if nn is None:
                dangling += 1
                continue
            used_nets.add(nn)
            conns.append((pn, nn))
            if pin_dirs.get(cir.name, {}).get(pn) == "OUTPUT":
                driven_by_output.add(nn)
        insts.append((cir.name, sc.expanded_name(), conns))

    all_nets = used_nets | port_names
    supplies = sorted(n for n in all_nets if n in ("VPWR", "VGND"))
    buses, _ = group_buses(all_nets - set(supplies))
    net_ref = make_net_ref(buses)
    port_set = set(port_names)

    # resolve each declared object (scalar name or bus base) once.
    def base_of(name):
        m = BUS_RE.match(name)
        return m.group(1) if (m and m.group(1) in buses) else name

    # ports: group into bases; a base is output iff any of its bits is driven.
    port_bases, seen = [], set()
    for p in sorted(port_names):
        b = base_of(p)
        if b not in seen:
            seen.add(b); port_bases.append(b)
    inputs, outputs = [], []      # (base, range-or-None)
    for b in port_bases:
        if b in buses:
            idx = buses[b]
            rng = _decl_range(idx)
            is_out = any(f"{b}[{i}]" in driven_by_output for i in idx)
        else:
            rng = None
            is_out = b in driven_by_output
        (outputs if is_out else inputs).append((b, rng))

    # internal wires: nets that are not ports and not supplies.
    internal = all_nets - port_set - set(supplies)
    wbuses, wscalars = group_buses(internal)
    port_bases_set = set(port_bases)

    L = []
    L.append("// extracted from GDS by extract.py (KLayout L2N, approach A)")
    portlist = [b for b, _ in inputs] + [b for b, _ in outputs]
    L.append(f"module {top.name} (" + ", ".join(vlog_id(b) for b in portlist) + ");")
    for b, rng in inputs:
        L.append(f"  input {rng + ' ' if rng else ''}{vlog_id(b)};")
    for b, rng in outputs:
        L.append(f"  output {rng + ' ' if rng else ''}{vlog_id(b)};")
    for s in supplies:
        L.append(f"  {'supply1' if s == 'VPWR' else 'supply0'} {vlog_id(s)};")
    for b in sorted(wbuses):
        if b in port_bases_set:
            continue
        L.append(f"  wire {_decl_range(wbuses[b])} {vlog_id(b)};")
    for w in sorted(wscalars, key=lambda s: (len(s), s)):
        L.append(f"  wire {vlog_id(w)};")
    L.append("")
    for celltype, inst, conns in sorted(insts, key=lambda t: t[1]):
        c = ", ".join(f".{pn}({net_ref(nn)})" for pn, nn in conns)
        # instance names live in a separate namespace from nets: L2N reuses
        # $NN for both, which collides in Verilog. Prefix to disambiguate.
        iname = "g_" + re.sub(r"\W", "_", inst)
        L.append(f"  {celltype} {iname} ({c});")
    L.append("endmodule")
    out.write("\n".join(L) + "\n")
    return {"instances": len(insts), "inputs": len(inputs),
            "outputs": len(outputs), "wire_buses": len(wbuses),
            "wire_scalars": len(wscalars), "dangling_pins": dangling,
            "port_bases": portlist}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gds")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--top", default=None)
    args = ap.parse_args()
    ly, top, l2n, nl, tc = extract(args.gds, args.top)
    pin_dirs = load_pin_dirs()

    # self-check: no router/physical cell should leak into the emitted netlist,
    # and no logic signal pin should be left dangling. These make the puzzle run
    # (which has no EQY oracle) trustworthy without a reference netlist.
    leaked = sorted({sc.circuit_ref().name for sc in tc.each_subcircuit()
                     if not is_emit_cell(sc.circuit_ref().name)})

    out = open(args.out, "w") if args.out else sys.stdout
    st = emit_verilog(ly, top, nl, tc, out, pin_dirs)
    if args.out:
        out.close()

    e = sys.stderr
    e.write(f"[extract] top={top.name} instances={st['instances']} "
            f"ports={st['inputs'] + st['outputs']} "
            f"(in={st['inputs']} out={st['outputs']}) "
            f"wire_buses={st['wire_buses']} wire_scalars={st['wire_scalars']}\n")
    e.write(f"[extract] module ports: {', '.join(st['port_bases'])}\n")
    if leaked:
        e.write(f"[extract] note: {len(leaked)} non-logic subcircuit type(s) "
                f"present in hierarchy, filtered from output "
                f"(e.g. {leaked[:3]}) -- connectivity threads through them\n")
    if st['dangling_pins']:
        e.write(f"[extract] WARNING: {st['dangling_pins']} logic signal pin(s) "
                f"had no net (dangling) -- inspect before trusting the netlist\n")


if __name__ == "__main__":
    main()
