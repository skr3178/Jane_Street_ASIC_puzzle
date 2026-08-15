chip
|
hardware description [verilog]
|
Netlist [NAND, XOR, NOR, flip flops]
|
EDA [pick and place routes]
|
Gates and locations
|
mask-final| active transitor layers




Layout | GDS
|
Netlist (determine task 1)
|
Circuit Purpose (task 2)
|
Output story

---

# Session summary — 2026-08-12

## warmup 04_final.gds vs puzzle.gds

| | warmup | puzzle |
|---|---|---|
| top cell | `adder_demo` | `puzzle` |
| die size | 100 × 100 µm | 200 × 352.7 µm (7× area) |
| std-cell types | 18 | 69 (all 18 warm-up types included) |
| VIA cells | 8 | 9 (all 8 included, + `VIA_M1M2_PR_MR`) |
| layers | — | + `200/0`, `66/15`, `81/23` |
| extra cells | — | `INTERNAL_3`, `INTERNAL_7` (inert, layer 200/0) |
| std cells (expanded) | ~380 | 1,618 (676 tap + 204 decap + 728 logic) |
| flip-flops | 16 | 92 |

## puzzle I/O

| signal | dir | notes |
|---|---|---|
| `clk`, `rst_n`, `enable`, `I` | in | `I` = 1-bit serial, left edge |
| `O[7:0]` | out | ASCII; example VCD decodes to `TRY AGAIN` ×2 |
| `success` | out | goal: drive high; stays 0 in example (242-bit `I` stream) |

## my yosys netlist vs shipped 01_netlist.v

| | mine | theirs |
|---|---|---|
| total cells | 61 | 230 |
| mux2 / dfrtp | 16 / 16 | 16 / 16 (exact match) |
| combinational | 27 | 44 |
| non-inverting share | 30% | 68% |
| drive strengths | all `_1` | mostly `_2`, clk `_16` |
| taps / decaps / clkbuf | 0 | 93 / 58 / 3 (post-PnR stages) |
| `abc -D` 100–2000 ps sweep | byte-identical output | — |

## formal equivalence (EQY, sat strategy, <1 s each)

| gold | gate | result |
|---|---|---|
| `00_source.v` (RTL) | `eqc/my_netlist.v` | ✔ PASS |
| `01_netlist.v` (shipped) | `eqc/my_netlist.v` | ✔ PASS (1 partition, 82 matched points) |

## task 1 — GDS → netlist extraction (`extract/`)

Approach A: KLayout `LayoutToNetlist` connectivity engine, cells kept as
subcircuits (see `extract/README.md`). Pure `python3` + pip `pya`.

| check | result |
|---|---|
| `extract.py warmup/04_final.gds` instance histogram vs `01_netlist.v` | ✔ exact (79 logic cells) |
| EQY `extracted_04.v` ≡ `01_netlist.v` | ✔ **PASS** (sat, partition `adder_demo.S`) |
| negative control (misroute one flop D) | ✔ FAIL w/ counterexample — gate discriminates |
| puzzle geometry coverage | ✔ all 13 ports on 70/5; 6 conb_1; 4 cell orientations — all handled by warmup-proven code |

Pipeline proven on warmup ground truth.

### puzzle extraction (done — `extract/puzzle/extracted_puzzle.v`)

`extract.py puzzle.gds` ran in 0.25 s. No EQY oracle exists for the puzzle, so
structural self-checks are the trust signal — all green:

| check | result |
|---|---|
| logic instances | 728 (matches GDS) |
| sequential cells | 92/92 exact: 84 dfrtp_2 + 4 dfstp_2 + 4 dfxtp_2 |
| tie cells conb_1 | 6 |
| interface | `puzzle(I, clk, enable, rst_n, O, success)` |
| `O` bus | `output [7:0] O;` (bus fix held on real design) |
| dangling signal pins | 0 |

Next: task 2 — key-search harness (BMC for the `I` sequence → `success`), then
simulate the output generator for the answer string.

## EQY + sky130 liberty gotchas

| problem | fix |
|---|---|
| `dlclkp` has no function attr | `read_liberty -wb -ignore_miss_dir -ignore_miss_func -ignore_miss_data_latch` |
| `tapvpwrvgnd` absent from liberty | Verilog stub with dummy `wire _stub_;` body (empty module → auto-blackbox) |
| `decap_3` in liberty as blackbox | don't stub; `delete */t:sky130_fd_sc_hd__decap_3` |
| whitebox cells stay boxed | `flatten -wb` after `prep` |
| leftover cell-module defs | `delete sky130_*` before `opt_clean -purge` |

## tooling

| tool | status |
|---|---|
| KLayout GUI + batch | `/usr/bin/klayout` 0.30.10; `-r` needs a real `.py` path |
| KLayout Python (pip) | 0.30.10, bare `import pya` works, db-only |
| yosys / eqy / sby | 0.62 / ok, in `nix-shell ~/Downloads/tiny-gpu/librelane` |
| sky130 liberty | `~/.ciel/ciel/sky130/versions/8afc8346*/sky130A/libs.ref/sky130_fd_sc_hd/lib/` |
| KlayoutClaw MCP | 127.0.0.1:8765, lives inside KLayout GUI — GUI must be running |

Files: [eqc/](eqc/) (synth.ys, netlists, .eqy configs) · [blog-post.md](blog-post.md) ·
[submission.md](submission.md) · deadline **2026-09-04**

## Logic chains
1. 00_source.v ≡ my_netlist.v — proven by EQY (PASS)
2. my_netlist.v ≡ 01_netlist.v — proven by EQY (PASS)
3. Therefore 00_source.v ≡ 01_netlist.v — by transitivity
4. Each SVG was generated mechanically from its .v with no hand edits — so the pictures depict those proven-equal circuits


## TASK 1 — "What is it?"          (extraction)

  polygons  ──▶  parts list + wiring
  
  puzzle.gds ──▶ netlist.v
  
  like: photographing a circuit board and
        writing down every chip and every wire


## TASK 2 — "What does it do?"     (understanding)

  parts list  ──▶  intent
  
  netlist.v ──▶ "it checks if A + B == 496"
  
  like: reading those 700 parts and realizing
        it's a lock waiting for a combination


## Most important finding for your challenge

- 04_final.gds appears to be an excellent reference/test case for developing your GDS→netlist extraction pipeline.
- It is much smaller:
04_final.gds
~230 functional standard-cell instances
- 16 sequential cells
whereas puzzle.gds is around an order of magnitude larger.

## Build pipeline

04_final.gds
      ↓
SKY130 LEF/GDS cell library
      ↓
KLayout LVS extraction
      ↓
cell instances + nets
      ↓
sky130_fd_sc_hd netlist
      ↓
compare against 01_netlist.v
      ↓
EQY / formal equivalence


## Challenge progress

DONE:    00_source.v ──yosys──▶ my_netlist.v ══EQY══ 01_netlist.v     (forward + proof)
DONE:    01_netlist.v ──SAT──▶ "a+b==496"                             (task 2, blind)
NOT DONE: 04_final.gds ──????──▶ extracted.v ══EQY══ 01_netlist.v     (task 1 — the pipeline you listed)


## possible options 

#	approach	engine	output	fit for us
A	KLayout LayoutToNetlist, cells opaque	pip klayout.db (installed)	cell-level netlist directly	✅ best — right abstraction, native to our tooling, no round-trip
B	Magic hierarchical extract → ext2spice → SPICE→Verilog	Magic (nix devshell)	SPICE .subckt calls → convert	⚠️ viable plan B — extra SPICE→Verilog step
C	KLayout LVS deck sky130.lylvs	KLayout (in PDK)	transistor-level SPICE	❌ wrong abstraction — MOSFETs, not cells
D	Magic flat extract → ext2spice	Magic	transistor-level SPICE	❌ wrong abstraction + must re-cluster gates
E	hand-write a polygon tracer	our Python from scratch	whatever we build	❌ reinvents L2N; only if A/B both fail

## challenge outputs

python3 extract.py warmup/04_final.gds → extracted_04.v
  • 79 logic cells, instance histogram IDENTICAL to 01_netlist.v
  • 0 dangling pins

EQY  extracted_04.v ≡ 01_netlist.v
  • ✔ PASS  (SAT strategy, partition adder_demo.S)

negative control (misroute one flip-flop D input)
  • ✔ FAIL with counterexample  → the check can actually catch errors

## OUTPUT comparative

                          total  logic  flops  clkbuf  mux2  comb   tap  decap
my_netlist (forward)        61     61     16      0      16    29     0     0
extracted_04 (reverse)      79     79     16      3      16    44     0     0
01_netlist (Jane Street)   230     79     16      3      16    44    93    58

## Extraction process

00_source.v ──yosys(forward)──▶ my_netlist.v   (61 cells)  ═══╗
                                                              ╠══ all EQY-equal
04_final.gds ──extract(reverse)─▶ extracted_04.v (79 cells) ═══╣
                                                              ║
                              Jane Street ─▶ 01_netlist.v  (gold) ═╝


## GDS checked

category      GDS   extracted
flop           92      92      OK
mux            21      21      OK
clkbuf         32      32      OK
tie             6       6      OK
comb          577     577      OK
──────────────────────────────
total logic   728     728      OK

66 distinct cell types, 0 mismatches


                 extracted   GDS
dfrtp_2             84        84     ← reset flops
dfstp_2              4         4     ← set flops
dfxtp_2              4         4     ← plain flops (no set/reset)
─────────────────────────────────
total sequential    92        92    ✓


## check result
logic instances	728 (matches GDS)
sequential cells	92/92, all three types exact
tie cells (conb_1)	6
module interface	puzzle(I, clk, enable, rst_n, O, success)
O bus	output [7:0] O; — bus fix held on the real design
dangling signal pins	0
escaped-scalar bus leaks	0


## extracted with phy too

extract_with_phys.py  04_final.gds → extracted_04_with_phys.v

               mine    01_netlist.v
tapvpwrvgnd     93   =     93
decap           58   =     58
dfrtp           16   =     16
mux2            16   =     16
clkbuf           3   =      3
... every type ...  identical
─────────────────────────────
total          230   =    230     HISTOGRAM BYTE-IDENTICAL
EQY  extracted_04_with_phys.v ≡ 01_netlist.v   ✔ PASS

## Jane Street's wording                          our label        status
─────────────────────────────────────────────────────────────────────
"recover a netlist from the layout"        →   Task 1           ✅ done
"figure out the circuit's true purpose"    →   Task 2a          ← we're here
"tease out the output it's looking for,
 find the string value"                    →   Task 2b          not started


# Checks
check	catches	puzzle result
cell histogram vs GDS	missing/extra cells	✅ 728/728 exact, 66 types
dangling-pin census (mine)	a pin with no net	✅ 0
unnamed-pin check (mine)	phantom internal-node pins	⚠️ 1 (g__279, handled + flagged)
yosys check — multi-driver	shorts (2 nets merged)	✅ 0
yosys check — comb loops	feedback errors	✅ 0
yosys check — undriven	floating/split nets	⚠️ 1 ($1447)


## magic tool

Magic says:   a31oi.A1  ─┐
              a311o.A1  ─┼─ ALL ONE NET ── nor3_2.C ── (driven by and2_2.X)
              nor3_2.C  ─┘

Our tool says: a31oi.A1, a311o.A1  → $1447  (undriven!)   ← SPLIT
               nor3_2.C            → $1419  (driven)       ← from the net above

Magic's a31oi_2 subckt port order: A3 B1 Y A1 A2 …
Magic's instance connections: A3=nand2b/Y, B1=and3b/C, Y=o31a/A2, A1=nor3_2_1/C, A2=o32ai/B1



---

## Extraction trust — 6-step validation (task 1)

Netlists are compared **formally** (miter/EQY), never textually. "Differ" = a SAT
solver finds a counterexample; a matching cell histogram is not proof of equivalence.

| # | step | what we did | status |
|---|---|---|---|
| 1 | Calibrate on ground truth | Extracted `04_final.gds`, proved **EQY PASS** vs golden `01_netlist.v` (same PDK/layers/geometry as puzzle) | ✅ |
| 2 | Negative control | Misrouted one flop's D input → EQY **FAIL with counterexample** | ✅ |
| 3 | Independent methods + formal cross-check | KLayout-L2N (ours) + **Magic** + **HAL** agree (728 cells / 92 FF / I/O). EQY on warmup ✅; on puzzle, targeted formal check on the one disputed net | ⚠️ partial (full netgen LVS on puzzle segfaulted; covered by step 6) |
| 4 | Adjudicate disagreements at the geometry | `$1447`/`$1419` dispute → GDS polygons (>200 nm gap), Magic revealed internal-li1 feedthrough, fixed at the geometry | ✅ |
| 5 | Method-independent invariants | histogram = GDS exactly (728 / 66 types); 0 dangling; 0 shorts; 0 undriven (after fix); 0 comb loops; ports = pads (13 on 70/5) | ✅ |
| 6 | Golden trace (final arbiter) | Replayed `example_inputs.vcd` through extracted netlist + reference cells → **"TRY AGAIN" ×2, success=0, exact match** | ✅ |

**Conclusion: task 1 (extraction) is validated and nothing is pending on it.**
Step 6 (golden trace) is the decisive arbiter for the puzzle and it passed, which
also covers the one partial item in step 3.

### Task status

| task | state |
|---|---|
| 1 — GDS → netlist (extraction) | ✅ done & trusted |
| 2a — circuit purpose | ✅ shape recovered (serial checksum/hash lock, 92-bit state, `success` = registered check over 57 state bits) |
| 2b — the key (`I` → success) | ✅ **SOLVED** — `cover(success)` key confirmed on the reference model: `success=1`, `O = (* TWO STARS *)` |

---

## SOLVED — answer: `(* TWO STARS *)`

An OCaml comment `(* ... *)` (Jane Street's language), emitted on `O[7:0]` in place
of "TRY AGAIN" once the chip is unlocked. Full write-up in `SOLUTION.md`.

### Method (task 2b, end to end)

1. **Behavioral validation first** (`behavior_check/`): simulate `extracted_puzzle.v`
   with the sky130 **reference** cell models (no `USE_POWER_PINS` → power-less cells
   match our netlist) driven by the exact `example_inputs.vcd` waveform. Reproduced
   `O="TRY AGAIN"` ×2, `success=0` — behavioral proof the netlist is correct and the
   simulation harness is trustworthy. This is the oracle for everything downstream.

2. **Decode the protocol from the example VCD**: 3-cycle reset (`rst_n=0`), 1 idle
   cycle, then `enable=1` and shift the key in 1 bit/cycle. (The example runs TWO
   failed 121-bit attempts → "TRY AGAIN" twice.) A wrong reset length gives garbage
   `O` — getting this right is essential.

3. **Formal key search** (`key_search/`, OSS CAD Suite): SymbiYosys `mode cover`
   with `cover(success)`, model built via `read_liberty -wb` + `flatten -wb` +
   `prep`, solver **bitwuzla**. Reaches `success` at depth 127 in ~12 s and emits
   an accepting `I` sequence.

4. **Confirm on the reference model** (`debug_S1/full.v`): replay the key through the
   reference sky130 sim. `success` pulses high (~cycle 125) and `O` spells
   **`(* TWO STARS *)`**. The 122-bit unlock key is `SOLUTION_key_bits.txt`.

### Debugging gotchas that were the whole battle

| symptom | real cause | fix |
|---|---|---|
| key gives garbage `O` on reference | wrong protocol (1-cycle reset, `enable=1` always) | rebuild harness with 3-cycle reset + idle + enable (from the VCD) |
| key "fails" on reference (`success=0`) but passes on `-wb` | **replay off-by-one** — sby drives `PI_I <= key[c]` (non-blocking → next cycle) | apply the key with **+1 cycle offset** |
| decoder reports `success=0` even when it fired | `success` is a **pulse**, not a latch | check "ever high" (latch it), not the final value |
| suspected `-wb` ≠ reference model | S1 test (known input → known output) proved `-wb` model is **correct** | no model bug; the issues above were the real blockers |

The decisive diagnostic was **S1** (from `debug_plan.md`): running the example's
*known* input through the `-wb` model and confirming it also produces "TRY AGAIN".
That isolated the problem to the replay, not the model — turning a suspected
deep model discrepancy into a one-line offset fix.

### Easter eggs found

- `example_inputs.vcd` header date `Dec 31 23:59:60 2016` — a real **leap second** (`:60`).
- VCD version string: "Leave no stone unturned!"
- The answer itself is an OCaml comment.

---

## Netlist-analysis toolbox — "what does this chip do?" (done vs pending)

All operate on the validated `extract/puzzle/extracted_puzzle.v`. ✅ = done, ⬜ = pending.

### Structure recovery (tells us the *shape*)

| tool / method | purpose | status | finding |
|---|---|---|---|
| HAL `hal_py` API | load netlist + liberty, script analysis | ✅ | 728 cells, 92 FF confirmed |
| HAL DANA / dataflow | recover registers / word-level datapath | ✅ | state **fragmented** — no clean registers |
| HAL `solve_fsm` | extract FSM state-transition graph | ✅ | **no isolable FSM/counter** — entangled state |
| Yosys cone tracing (`%ci*`) | success / O fan-in cones | ✅ | success cone = 79 FF; O cone = 92 FF |
| netlistsvg / Graphviz | render topology | ✅ | diagrams in `diagrams/puzzle/` |
| HAL GUI (interactive graph) | click-through tracing | ⬜ | headless only so far |
| HAL `module_identification` | recover lost hierarchy / known blocks | ⬜ | |
| HAL graph clustering / community | find modules by connectivity | ⬜ | |

### Function extraction (tells us the *purpose* — the open work)

| tool / method | purpose | status | finding |
|---|---|---|---|
| **Linearity test** (Δ-input superposition sim) | is the state-fold linear (LFSR/CRC) or non-linear? | ✅ | **NON-LINEAR** — 30/30 trials, 51/92 bits non-linear → custom one-way hash, not CRC/LFSR (`hash/linearity/`) |
| Yosys `sat` on the `$4240` check | extract the accept condition / target constant | ⬜ (started) | |
| ABC `collapse` / BDD | canonical form of the check cone → equality vs complex | ⬜ | |
| Yosys `freduce` / `submod` | simplify + isolate the check logic | ⬜ | |
| HAL `boolean_influence` | rank which input cycles drive `success` | ⬜ | |

### Formal / behavioral (already used to *solve*, not to *understand*)

| tool / method | purpose | status | finding |
|---|---|---|---|
| Yosys + EQY | equivalence proofs (extraction validation) | ✅ | warmup PASS; negative control FAILs |
| SymbiYosys `cover(success)` + bitwuzla | synthesize the unlock key | ✅ | 122-bit key found |
| Icarus Verilog + sky130 models | reference simulation | ✅ | golden trace + key → `(* TWO STARS *)` |
| Verilator | faster gate-level sim | ⬜ | iverilog used instead |
| GTKWave dual-trace diff | accept vs reject internals, eyes-on | ⬜ | |

**Summary:** structure recovery is essentially complete (→ "scrambled hash lock").
Function extraction is now largely done: the **linearity test** answered the decisive
question — the state-fold is **NON-LINEAR** (a custom one-way hash, not a CRC/LFSR),
which is *why* the key had to be found by search (BMC), not algebra. The only
remaining extractable property is the **57-bit target constant** the `success` check
compares against.
