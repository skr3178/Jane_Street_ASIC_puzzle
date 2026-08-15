# Dump (instance name, cell type, x, y in um) for every logic cell, using the same L2N run as extract.py
import sys, os, json
sys.path.insert(0, "extract")
import extract as E
ly, top, l2n, nl, tc = E.extract("../puzzle.gds")
dbu = ly.dbu
rows = []
for sc in tc.each_subcircuit():
    cir = sc.circuit_ref()
    if not E.is_logic_cell(cir.name): continue
    t = sc.trans
    rows.append((E.vlog_id(sc.expanded_name()), cir.name.replace("sky130_fd_sc_hd__",""), t.disp.x*dbu, t.disp.y*dbu))
json.dump(rows, open("recon/opam/placement.json","w"))
print(len(rows), "cells;", rows[:3])
