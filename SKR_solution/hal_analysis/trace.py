import hal_py, sys
from collections import deque, Counter
hal_py.plugin_manager.load_all_plugins()
gl = hal_py.GateLibraryManager.load(sys.argv[1])
nl = hal_py.NetlistFactory.load_netlist(sys.argv[2], gl)
FF = hal_py.GateTypeProperty.ff
gates = nl.get_gates()
ffs = set(g for g in gates if g.get_type().has_property(FF))

def gtype(g): return g.get_type().get_name().replace("sky130_fd_sc_hd__","")

# 1) what drives success?
succ = [n for n in nl.get_nets() if n.get_name()=="success"][0]
drv = succ.get_sources()
print("success driven by:", [(gtype(s.get_gate()), s.get_pin().get_name()) for s in drv])

# 2) back-trace combinational fan-in of a net until hitting FF outputs / inputs
def comb_fanin_ffs(start_net, maxdepth=200):
    seen=set(); srcffs=set(); frontier=deque([start_net]); depth=0
    visited_nets=set()
    while frontier:
        net=frontier.popleft()
        if net.get_id() in visited_nets: continue
        visited_nets.add(net.get_id())
        for s in net.get_sources():
            g=s.get_gate()
            if g in ffs:
                srcffs.add(g)          # state bit feeds here; stop (don't cross FF)
            else:
                for ie in g.get_fan_in_endpoints():
                    frontier.append(ie.get_net())
    return srcffs

# success FF's D cone: which state bits + inputs feed the success register's D
succ_ff = drv[0].get_gate()
dpin = [e for e in succ_ff.get_fan_in_endpoints() if e.get_pin().get_name()=="D"]
dnet = dpin[0].get_net()
sf = comb_fanin_ffs(dnet)
print("success-register D depends on %d state FFs" % len(sf))

# 3) I influence: which FFs' D cone includes primary input I
Inet=[n for n in nl.get_nets() if n.get_name()=="I"][0]
# forward: what does I reach (comb) -> which FF data pins
def forward_to_ffs(start_net):
    reached=set(); vis=set(); fr=deque([start_net])
    while fr:
        net=fr.popleft()
        if net.get_id() in vis: continue
        vis.add(net.get_id())
        for d in net.get_destinations():
            g=d.get_gate()
            if g in ffs and d.get_pin().get_name() in ("D","SET_B","RESET_B","SCD","SCE"):
                reached.add(g)
            elif g not in ffs:
                for oe in g.get_fan_out_endpoints():
                    fr.append(oe.get_net())
    return reached
Iffs = forward_to_ffs(Inet)
print("FFs whose data cone includes I (serial input):", len(Iffs))

# 4) enable / mux structure: do FFs recirculate (Q feeds own D cone via mux)?
muxes=[g for g in gates if "mux" in gtype(g)]
print("mux2 cells:", len(muxes), "| xor/xnor:", sum(1 for g in gates if gtype(g).startswith(("xor","xnor"))))
