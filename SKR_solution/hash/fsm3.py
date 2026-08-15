import hal_py, sys
from collections import deque
hal_py.plugin_manager.load_all_plugins()
import dataflow, solve_fsm
gl=hal_py.GateLibraryManager.load(sys.argv[1]); nl=hal_py.NetlistFactory.load_netlist(sys.argv[2],gl)
FF=hal_py.GateTypeProperty.ff
ffset=set(g for g in nl.get_gates() if g.get_type().has_property(FF))
res=dataflow.analyze(dataflow.Configuration(nl).with_flip_flops().with_stage_identification())
groups=res.get_groups()
def dpins(g): return [ep for ep in g.get_fan_in_endpoints() if ep.get_pin().get_name()=='D']
def tl(state):
    comb=set(); seen=set(); ext_ff=set(); fr=deque()
    for g in state:
        for ep in dpins(g):
            if ep.get_net(): fr.append(ep.get_net())
    while fr:
        net=fr.popleft()
        if net.get_id() in seen: continue
        seen.add(net.get_id())
        for src in net.get_sources():
            gg=src.get_gate()
            if gg in ffset:
                if gg not in state: ext_ff.add(gg)   # reads an external flop
                continue
            if gg not in comb:
                comb.add(gg)
                for ie in gg.get_fan_in_endpoints():
                    if ie.get_net(): fr.append(ie.get_net())
    return list(comb), ext_ff
# rank groups by self-containment: fewest external-flop dependencies
cands=[]
for sz,gid in sorted(((len(v),k) for k,v in groups.items()), reverse=True):
    if sz<3 or sz>7: continue
    t,ext=tl(list(groups[gid]))
    cands.append((len(ext), sz, gid, len(t)))
cands.sort()
print("group self-containment (external-flops read, size, id, tl-gates):")
for e,sz,gid,ng in cands: print(f"   group {gid}: reads {e} external flops, {sz} ff, {ng} comb gates")
# solve the MOST self-contained one only
e,sz,gid,ng=cands[0]
print(f"\nsolving most self-contained: group {gid} ({sz} ff, reads {e} external flops)")
state=list(groups[gid]); t,_=tl(state)
r=solve_fsm.solve_fsm_brute_force(nl, state, t, f"{sys.argv[3]}/fsm_best.dot")
if r is None: print("  FAILED / not a clean FSM")
else:
    deg=[len(v) for v in r.values()]
    print(f"  {len(r)} reachable states, out-deg min/max/avg {min(deg)}/{max(deg)}/{sum(deg)/len(deg):.1f}")
    print("  (linear chain ~ counter; dense ~ entangled datapath)")
