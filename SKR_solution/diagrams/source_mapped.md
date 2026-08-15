# Diagram → Source Map

Filenames encode lineage as `<parent-stem>.<what>.svg` — the part before the first dot is the
warmup Verilog file the diagram was generated from (`00_source` = `warmup/00_source.v`,
`01_netlist` = `warmup/01_netlist.v`).

```text
warmup/00_source.v  (RTL, behavioral)
   │
   │  yosys synth (stopped before tech mapping) → write_json → netlistsvg
   │
   └──▶ 00_source.generic_gates.svg                 79 generic cells: DFFE/AND/OR/XOR/NOT


warmup/01_netlist.v  (sky130 structural, Jane Street's)
   │
   │  yosys show (cells drawn as-is, liberty for port directions)
   │
   ├──▶ 01_netlist.sky130_cells_full.svg        (+ .dot)   all 79 logic cells, taps/decaps stripped
   ├──▶ 01_netlist.sky130_adder_comparator.svg  (+ .dot)   subset: mux/dff/clkbuf also deleted → 41-cell comb. cloud
   ├──▶ 01_netlist.sky130_bit_slice.svg         (+ .dot)   subset: 4 cells only (sr_a/_08_,_09_,_16_,_17_)
   │
   │  read_liberty -wb → flatten (cells → Boolean primitives) → write_json → netlistsvg
   │
   └──▶ 01_netlist.generic_gates.svg                209 generic primitives
```

## Table

| diagram | source | pipeline | style | contents |
|---|---|---|---|---|
| [00_source.generic_gates.svg](warmup/00_source.generic_gates.svg) | `00_source.v` | `synth` → `write_json` → netlistsvg | generic gate symbols | 79 cells: 16 DFFE, 23 AND, 19 OR, 15 XOR, 6 NOT |
| [01_netlist.sky130_cells_full.svg](warmup/01_netlist.sky130_cells_full.svg) | `01_netlist.v` | `show` | sky130 cell boxes | all 79 logic cells (taps/decaps stripped) |
| [01_netlist.sky130_adder_comparator.svg](warmup/01_netlist.sky130_adder_comparator.svg) | `01_netlist.v` | `show` (mux/dff/clkbuf also deleted) | sky130 cell boxes | 41-cell adder + ==496 comparator cloud |
| [01_netlist.sky130_bit_slice.svg](warmup/01_netlist.sky130_bit_slice.svg) | `01_netlist.v` | `show` on 4 named cells | sky130 cell boxes | 2 bits of shift register `sr_a` (mux → dfrtp loop) |
| [01_netlist.generic_gates.svg](warmup/01_netlist.generic_gates.svg) | `01_netlist.v` | `read_liberty -wb` → `flatten` → netlistsvg | generic gate symbols | 209 primitives: 86 AND, 65 NOT, 42 OR, 16 DFF |

`.dot` files are graphviz sources for the three `show` diagrams — re-render with `dot -Tsvg`/`-Tpng`.

## Puzzle diagrams (`puzzle/`)

Rendered from `../extract/puzzle/extracted_puzzle.v` (728 logic cells, 92 flops). At this
scale the full schematics are reference-only; the `success_cone` views (484 cells /
79 flops feeding `success`, output generator removed) are the readable ones.

| diagram | scope | style | scale |
|---|---|---|---|
| [puzzle/puzzle.full.sky130.svg](puzzle/puzzle.full.sky130.svg) | whole chip | sky130 cell boxes | 728 cells |
| [puzzle/puzzle.full.generic_gates.svg](puzzle/puzzle.full.generic_gates.svg) | whole chip | generic gate symbols | ~1900 gates |
| [puzzle/puzzle.success_cone.sky130.svg](puzzle/puzzle.success_cone.sky130.svg) | `success` cone only | sky130 cell boxes | 484 cells |
| [puzzle/puzzle.success_cone.generic_gates.svg](puzzle/puzzle.success_cone.generic_gates.svg) | `success` cone only | generic gate symbols | ~1200 gates |

`.json` files alongside are the yosys `write_json` sources for netlistsvg (re-render
with `netlistsvg <f>.json -o <f>.svg`, then re-patch the white background).

## Equivalence

The two `generic_gates` diagrams render the **same EQY-proven function** (see `../eqc/`):
`00_source.v` ≡ `my_netlist.v` ≡ `01_netlist.v`, both proofs PASS. 79 vs 209 gates is
technology mapping made visible — every difference is optimization, not behavior.

## Notes

- `02_netlist_with_power_rails.v` fed nothing — it is `01_netlist.v` plus `VPWR`/`VGND`
  hookups; same logic, noisier drawing.
- The three `show` diagrams draw only `01_netlist.v` instances, but the sky130 liberty supplied
  port directions — without it, yosys guesses and draws `Q` as an input.
- netlistsvg outputs a transparent background (invisible on dark viewers); both generic SVGs
  have a white `<rect>` patched in. Re-patch after regenerating:
  `sed -i 's|\(<svg[^>]*>\)|\1<rect width="100%" height="100%" fill="white" stroke="none"/>|' file.svg`
