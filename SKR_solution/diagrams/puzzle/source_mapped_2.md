# Puzzle Diagram → Source Map

Every diagram in this folder derives from one original file: `puzzle.gds`, via the
recovered netlist `../../extract/puzzle/extracted_puzzle.v`. Nothing here comes from a
Jane-Street-supplied netlist — there is none for the puzzle (that's task 1's whole
point). Naming: `puzzle.<scope>.<style>.<ext>`.

## Provenance chain

```text
puzzle.gds  (Jane Street, the only given)
   │
   │  extract.py  (KLayout LayoutToNetlist, approach A)
   ▼
../../extract/puzzle/extracted_puzzle.v   728 logic cells, 92 flip-flops
   │
   ├─ yosys read_liberty -lib + write_json ─────────────▶ *.sky130.json     (cells as boxes)
   │        └─ netlistsvg ─────────────────────────────▶ *.sky130.svg
   │
   ├─ yosys read_liberty -wb + flatten -wb + write_json ▶ *.generic_gates.json (decomposed to AND/OR/NOT/DFF)
   │        └─ netlistsvg ─────────────────────────────▶ *.generic_gates.svg
   │
   └─ success cone = select o:success %ci* (prune the rest) before either path
            └────────────────────────────────────────▶ *.success_cone.* variants
```

## Files

| SVG | JSON source | scope | style | scale |
|---|---|---|---|---|
| [puzzle.full.sky130.svg](puzzle.full.sky130.svg) | [puzzle.full.sky130.json](puzzle.full.sky130.json) | whole chip | sky130 cell boxes | 728 cells |
| [puzzle.full.generic_gates.svg](puzzle.full.generic_gates.svg) | [puzzle.full.generic_gates.json](puzzle.full.generic_gates.json) | whole chip | generic gate symbols | ~1900 gates (3008 json objs) |
| [puzzle.success_cone.sky130.svg](puzzle.success_cone.sky130.svg) | [puzzle.success_cone.sky130.json](puzzle.success_cone.sky130.json) | `success` fan-in cone only | sky130 cell boxes | 484 cells |
| [puzzle.success_cone.generic_gates.svg](puzzle.success_cone.generic_gates.svg) | [puzzle.success_cone.generic_gates.json](puzzle.success_cone.generic_gates.json) | `success` fan-in cone only | generic gate symbols | ~1200 gates (1934 json objs) |

## Original files referenced

| role | path |
|---|---|
| layout (the only given) | `../../../puzzle.gds` |
| recovered netlist | `../../extract/puzzle/extracted_puzzle.v` |
| extractor | `../../extract/extract.py` |
| sky130 liberty (cell functions) | `~/.ciel/ciel/sky130/versions/8afc8346*/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib` |

## Reading guide

- **Full views are reference-only** at 728 cells — even zoomed, ~1900 gates is a
  thicket. Use them to locate, not to read.
- **Success-cone views are the readable ones**: they keep only the 484 cells / 79
  flip-flops that feed `success` and drop the output generator entirely. This is
  the "lock" logic for task 2a. (All 92 flops feed `O`; the 79 success-flops are a
  subset, so the output generator reads the lock but doesn't drive it.)

## Re-rendering

```bash
netlistsvg <file>.json -o <file>.svg
# netlistsvg outputs a transparent background (invisible on dark viewers); re-patch:
sed -i 's|\(<svg[^>]*>\)|\1<rect width="100%" height="100%" fill="white" stroke="none"/>|' <file>.svg
```

To regenerate the JSONs, see the yosys `read_liberty`/`flatten -wb`/`write_json`
recipe in the provenance chain above; the success-cone prune is
`select -set drop t:* o:success %ci* %d; delete @drop; opt_clean`.

## Caveat carried from extraction

The netlist has one flagged anomaly: net `$1419` touches an unlabeled internal node
of `a31oi_2 g__279` (skipped as a non-pin connection — likely a li1 feedthrough
artifact, possibly a deliberate tap). These diagrams reflect the cell as a clean
library blackbox, i.e. that stray connection is not drawn.
