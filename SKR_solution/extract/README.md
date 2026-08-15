# GDS → Netlist Extractor (task 1)

Recovers a cell-level Verilog netlist from a sky130 GDS layout by tracing metal
connectivity between standard-cell instances. **Approach A**: drive KLayout's
`LayoutToNetlist` (L2N) engine — the same machinery its LVS uses — in pure
connectivity mode. No transistor extraction, no gate re-recognition: the cell
hierarchy survives in the GDS, so each std-cell placement is already a named
instance; we only trace the wires between their pins.

## Why this works

- Cells are **named subcells** in the GDS (`sky130_fd_sc_hd__*`); only net names
  were stripped.
- Each cell definition carries its **pin labels inside it** (li1.label 67/5:
  `A`, `B`, `X`, `Q`, …), so L2N names every instance pin automatically.
- Tracing only conductor layers (li1→met5 + vias) keeps cells opaque:
  transistors live on poly/diffusion, which we exclude, so a cell's input and
  output pins never short through it. Physics does the net separation.

## Usage

```bash
python3 extract.py <in.gds> -o <out.v> [--top NAME]
```

Pure `python3` + the pip `klayout` module (`import pya`). No nix, no GUI.

## Pipeline (in `extract.py`)

1. **Flatten non-logic cells** — router `VIA_*` arrays and physical fill
   (tap/decap/fill/diode) are flattened into the top so their via geometry
   participates in the trace instead of becoming opaque blackboxes.
2. **Register layers** — conductors li1, mcon, met1..met5, via1..via4 as polygon
   layers; li1/met1..met5 `.label` (datatype 5) as text layers.
3. **Declare connectivity** — intra-layer + the vertical via chain
   li1–mcon–met1–via1–met2–…–met5; attach each metal to its label layer so nets
   inherit pin/port names.
4. **`extract_netlist()`** — L2N returns a hierarchical netlist: top circuit with
   one SubCircuit per std cell, pins mapped to nets.
5. **Emit Verilog** — logic cells only (physical cells dropped); module ports
   from top-level labels, directions from the LEF (`DIRECTION INPUT/OUTPUT`);
   power pins (VPWR/VGND/VPB/VNB) omitted per `01_netlist.v` convention.

## Validation (the whole point)

| check | result |
|---|---|
| instance histogram vs `01_netlist.v` (logic cells) | **exact match** — 79 cells, every type/count |
| EQY formal equivalence `extracted_04.v` ≡ `01_netlist.v` | **PASS** (sat strategy, 1 partition `adder_demo.S`) |
| negative control (misroute one flop D input) | **FAIL** with counterexample — gate discriminates |

Equivalence config: `sample/extracted_vs_01.eqy` (reuses the liberty gotchas from
`../eqc/`). Run:

```bash
nix-shell ~/Downloads/tiny-gpu/librelane --run \
  "cd SKR_solution/extract/sample && eqy -f extracted_vs_01.eqy"
```

## Files

Shared tools (top level):
- `extract.py` — the extractor
- `extract_with_phys.py` — variant that also emits tap/decap (full 230-cell match)
- `README.md` — this file

`sample/` — warmup outputs:
- `extracted_04.v` — netlist recovered from `warmup/04_final.gds` (EQY-proven)
- `extracted_04_with_phys.v` — same, including physical cells (230 total)
- `extracted_vs_01.eqy` — equivalence config (gold = `01_netlist.v`, gate = extracted)

`puzzle/` — puzzle output:
- `extracted_puzzle.v` — netlist recovered from `puzzle.gds` (728 logic cells, 92 flops)

## Adversarial review (3 independent reviewers, read-only vs puzzle.gds)

Reviewed for failure modes the warmup can't exercise but the puzzle will:

- **Bus ports** — CONFIRMED BUG, fixed. `O[0..7]` labels would have emitted as 8
  escaped scalars `\O[0] `, which yosys treats as opaque names unrelated to a
  reference `output [7:0] O;` → primary output unmatched under LEC (false FAIL
  or silent skip). Fix: `group_buses`/`make_net_ref` coalesce them into
  `output [7:0] O;` with unescaped bit-selects `O[i]`. Unit-tested in isolation.
- **Orientation** — SAFE. Puzzle has 4 cell orientations (mirrored rows); L2N
  applies each instance transform to polygons and pin labels together, so naming
  is orientation-independent. The warmup also has all 4 and passed EQY.
- **Net numbering** — deterministic across processes (same sha256), so runs are
  diff-able (correctness is EQY's job regardless).
- **Port label coverage** — all 13 puzzle ports are on met3 (70/5), which
  `top_port_labels` scans; none missed.
- **conb_1 tie cells (6 in puzzle)** — handled: kept as instances with HI/LO,
  power pins dropped, constants resolved from liberty in EQY.
- **Flatten step was a silent no-op** — `Layout.flatten_cell` doesn't exist in
  this KLayout build; the call threw and was swallowed. REMOVED as dead code:
  L2N threads nets hierarchically through un-flattened VIA_* cells, and the
  emitter's `is_logic_cell` filter drops them. Self-check now reports the count
  of filtered non-logic subcircuits so this stays visible.

## Self-check

Because the puzzle run has no EQY oracle, `extract.py` prints diagnostics to
stderr: instance/port/wire counts, module port list, count of non-logic
subcircuits filtered out, and a WARNING if any logic signal pin is left dangling
(a symptom of a broken via thread). On the warmup: 79 instances, 0 dangling.

## Running on the puzzle

`python3 extract.py ../../puzzle.gds -o puzzle/extracted_puzzle.v` — same code path,
now bus-aware. Verified read-only that `puzzle.gds` introduces no via type,
layer, or cell family absent from the warmup. Per the puzzle rules, that run and
all puzzle-side analysis are user-driven.
