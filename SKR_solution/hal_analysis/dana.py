import hal_py, sys
hal_py.plugin_manager.load_all_plugins()
import dataflow
lib, nlpath = sys.argv[1], sys.argv[2]
gl = hal_py.GateLibraryManager.load(lib)
nl = hal_py.NetlistFactory.load_netlist(nlpath, gl)
cfg = dataflow.Configuration(nl)
cfg = cfg.with_flip_flops().with_min_group_size(1)
res = dataflow.analyze(cfg)
groups = res.get_groups()
print("=== DANA register groups: %d groups over 92 flip-flops ===" % len(groups))
sizes = {}
for gid, gates in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    n = len(gates)
    sizes[n] = sizes.get(n,0)+1
    print("  group %-4s : %2d flip-flops" % (gid, n))
print("--- size histogram (width -> #registers) ---")
for w in sorted(sizes, reverse=True):
    print("  %2d-bit x %d" % (w, sizes[w]))
print("total FFs grouped:", sum(len(g) for g in groups.values()))
