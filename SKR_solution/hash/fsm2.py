import hal_py, sys
from collections import deque
hal_py.plugin_manager.load_all_plugins()
import dataflow, solve_fsm
gl=hal_py.GateLibraryManager.load(sys.argv[1]); nl=hal_py.NetlistFactory.load_netlist(sys.argv[2],gl)
FF=hal_py.GateTypeProperty.ff
ffset=set(g for g in nl.get_gates() if g.get_type().has_property(FF))
# confirm D is now data
gt=gl.get_gate_type_by_name("sky130_fd_sc_hd__dfrtp_2")
print("dfrtp_2 D pin type now:", [p.get_type() for p in gt.get_pins() if p.get_name()=='D'])
res=dataflow.analyze(dataflow.Configuration(nl).with_flip_flops().with_stage_identification())
groups=res.get_groups()
def dpins(g): return [ep for ep in g.get_fan_in_endpoints() if ep.get_pin().get_name()=='D']
def tl(state):
    comb=set(); seen=set(); fr=deque()
    for g in state:
        for ep in dpins(g):
            if ep.get_net(): fr.append(ep.get_net())
    while fr:
        net=fr.popleft()
        if net.get_id() in seen: continue
        seen.add(net.get_id())
        for src in net.get_sources():
            gg=src.get_gate()
            if gg in ffset: continue
            if gg not in comb:
                comb.add(gg)
                for ie in gg.get_fan_in_endpoints():
                    if ie.get_net(): fr.append(ie.get_net())
    return list(comb)
for sz,gid in sorted(((len(v),k) for k,v in groups.items()), reverse=True):
    if sz<3 or sz>7: continue
    state=list(groups[gid]); t=tl(state)
    r=solve_fsm.solve_fsm_brute_force(nl, state, t, f"{sys.argv[3]}/fsm_g{gid}.dot")
    if r is None: print(f"group {gid} ({sz} ff, {len(t)} gates): solve FAILED"); continue
    deg=[len(v) for v in r.values()]
    print(f"group {gid} ({sz} ff): {len(r)} reachable states, out-deg min/max/avg {min(deg)}/{max(deg)}/{sum(deg)/len(deg):.1f}")
