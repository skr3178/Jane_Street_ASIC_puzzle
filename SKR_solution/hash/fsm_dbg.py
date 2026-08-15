import hal_py, sys
from collections import deque
hal_py.plugin_manager.load_all_plugins()
import dataflow, solve_fsm
gl=hal_py.GateLibraryManager.load(sys.argv[1]); nl=hal_py.NetlistFactory.load_netlist(sys.argv[2],gl)
FF=hal_py.GateTypeProperty.ff
ffset=set(g for g in nl.get_gates() if g.get_type().has_property(FF))
res=dataflow.analyze(dataflow.Configuration(nl).with_flip_flops().with_stage_identification())
groups=res.get_groups()
# smallest group with small transition logic
gid=min(groups, key=lambda k:len(groups[k]) if len(groups[k])>=3 else 999)
state=list(groups[gid])
print("state gates:", [g.get_name() for g in state], "| types:", [g.get_type().get_name() for g in state])
def dpins(g):
    return [ep for ep in g.get_fan_in_endpoints() if ep.get_pin().get_name()=='D']
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
t=tl(state)
print("transition_logic gates:", len(t))
print("=== calling solve_fsm_brute_force (raw) ===")
r=solve_fsm.solve_fsm_brute_force(nl, state, t, "")
print("return type:", type(r), "value:", r if r is None else ("map with %d entries"%len(r)))
