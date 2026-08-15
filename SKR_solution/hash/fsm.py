import hal_py, sys
from collections import deque
hal_py.plugin_manager.load_all_plugins()
import dataflow, solve_fsm
gl = hal_py.GateLibraryManager.load(sys.argv[1])
nl = hal_py.NetlistFactory.load_netlist(sys.argv[2], gl)
FF = hal_py.GateTypeProperty.ff
gates = nl.get_gates()
ffset = set(g for g in gates if g.get_type().has_property(FF))

# DANA register groups
res = dataflow.analyze(dataflow.Configuration(nl).with_flip_flops().with_stage_identification())
groups = res.get_groups()
sizes = sorted(((len(v), k) for k,v in groups.items()), reverse=True)
print("DANA groups by size:", [s for s,_ in sizes])

def data_pins(g):
    # flop data input pins (exclude clock/reset/set/enable)
    out=[]
    for ep in g.get_fan_in_endpoints():
        pt = ep.get_pin().get_type()
        if str(pt) in ("PinType.data","data") or ep.get_pin().get_name() in ("D",):
            out.append(ep)
    return out

def transition_logic(state_gates):
    # BFS backward from each state flop's data net, collect combinational gates,
    # stop at any flop (sequential boundary) or primary input.
    sg=set(state_gates); comb=set(); seen=set()
    frontier=deque()
    for g in state_gates:
        for ep in data_pins(g):
            net=ep.get_net()
            if net: frontier.append(net)
    while frontier:
        net=frontier.popleft()
        if net.get_id() in seen: continue
        seen.add(net.get_id())
        for src in net.get_sources():
            gg=src.get_gate()
            if gg in ffset:      # sequential boundary -> stop
                continue
            if gg not in comb:
                comb.add(gg)
                for ie in gg.get_fan_in_endpoints():
                    if ie.get_net(): frontier.append(ie.get_net())
    return list(comb)

# try solve_fsm on the largest brute-forceable groups (<=8 bits)
for sz,gid in sizes:
    if sz<3 or sz>8: continue
    state=list(groups[gid])
    tl=transition_logic(state)
    print(f"\n=== group {gid}: {sz} flops, transition_logic={len(tl)} comb gates ===")
    try:
        graph=f"{sys.argv[3]}/fsm_group{gid}.dot"
        tg=solve_fsm.solve_fsm_brute_force(nl, state, tl, graph)
        nstates=len(tg)
        ntrans=sum(len(v) for v in tg.values())
        print(f"   reachable states: {nstates}, transitions: {ntrans}  -> DOT: fsm_group{gid}.dot")
        # counter signature: each state has ~1-2 transitions, linear-ish
        deg=[len(v) for v in tg.values()]
        print(f"   out-degree min/max/avg: {min(deg)}/{max(deg)}/{sum(deg)/len(deg):.1f}" if deg else "   empty")
    except Exception as e:
        print("   solve_fsm failed:", str(e)[:120])
