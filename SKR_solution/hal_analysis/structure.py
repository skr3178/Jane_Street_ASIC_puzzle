import hal_py, sys
hal_py.plugin_manager.load_all_plugins()
import dataflow
gl = hal_py.GateLibraryManager.load(sys.argv[1])
nl = hal_py.NetlistFactory.load_netlist(sys.argv[2], gl)
FF = hal_py.GateTypeProperty.ff
gates = nl.get_gates()
ffs = [g for g in gates if g.get_type().has_property(FF)]

# --- DANA with fuller heuristics (no forced singletons) ---
cfg = dataflow.Configuration(nl).with_flip_flops().with_stage_identification().with_type_consistency()
res = dataflow.analyze(cfg)
groups = res.get_groups()
print("=== DANA (stage id + type consistency): %d groups ===" % len(groups))
from collections import Counter
h = Counter(len(g) for g in groups.values())
for w in sorted(h, reverse=True):
    print("  %2d-bit x %d" % (w, h[w]))

# --- shift-register chain check: how many FFs have Q -> next FF.D ? ---
def drives_ff_d(g):
    # does this FF's Q feed another FF's data pin (through only wires/buffers)?
    for ep in g.get_fan_out_endpoints():
        pass
    return None
# direct Q->D adjacency among FFs
ff_set=set(ffs)
qd_edges=0
for g in ffs:
    for out_ep in g.get_successors():
        if out_ep.get_gate() in ff_set:
            # is the destination pin a data pin (D)?
            if out_ep.get_pin().get_name() in ("D",):
                qd_edges+=1
print("direct FF.Q -> FF.D adjacencies:", qd_edges, "(of 92 FFs)")

# --- I fanout depth (serial input structure) ---
I = nl.get_net_by_id
inet = [n for n in nl.get_nets() if n.get_name()=="I"]
print("I net found:", bool(inet))
