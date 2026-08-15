# SOLUTION — Jane Street ASIC puzzle

## Answer

```
literal output:  (* TWO STARS *)
likely answer:   TWO STARS
```

When the chip is unlocked, the output generator emits `(* TWO STARS *)` on `O[7:0]`
(replacing "TRY AGAIN"). It is written as an **OCaml comment** `(* ... *)` — Jane
Street's language — so the string value is almost certainly **`TWO STARS`**, wrapped
in comment delimiters; the full literal emitted is `(* TWO STARS *)`. Final choice of
which to submit is a judgment call. Verified on the reference sky130 cell models (the
real-chip behavior): `success` goes high, and `O` spells `(* TWO STARS *)`.

## The unlock input (key)

122 bits fed serially on `I`, one bit per clock while `enable=1`, after the reset
protocol below (`SOLUTION_key_bits.txt`):

```
0000000101010000100000000000010101010000000000001010000001000001
0000001000001010000100000001000000100000100100010100000000
```

## Protocol (decoded from example_inputs.vcd)

```
cycles 0-2 : rst_n=0, enable=0    (reset held 3 cycles)
cycle  3   : rst_n=1, enable=0    (1 idle cycle)
cycle  4+  : rst_n=1, enable=1    (shift the 122-bit key in, 1 bit/cycle)
success goes high at cycle 125 (the cycle after the 121st board bit) and STAYS high; O reads "(* TWO STARS *)"
NOTE: the board is 121 cells (11x11); the 122nd bit is ignored by the chip (a don't-care).
```

## How it was solved (end to end)

1. **Task 1 — extraction**: `puzzle.gds` → `extracted_puzzle.v` via KLayout
   LayoutToNetlist (approach A). 728 cells, 92 flip-flops. Validated 6 ways
   (warmup EQY, negative control, Magic + HAL cross-checks, sanity invariants,
   and the golden trace reproducing "TRY AGAIN"). See `SKR_challenge.md`.
2. **Task 2a — the circuit's true purpose**: recovered from the netlist alone, in
   three deepening steps:
   - *structure* (HAL DANA + `solve_fsm`): no shift register / counter / FSM — one
     entangled 92-bit state (dependency graph: 801 edges, avg 8.7). See `hal_analysis/`.
   - *linearity* (Δ-input superposition sim): the state-fold is **non-linear**
     (30/30 trials); the non-linearity sits in the 57-bit hash core, while a
     low-weight sequencer drives the display. See `hash/linearity/`.
   - *exact recurrence* (symbolic ANF from netlist + Liberty): the literal per-bit
     update equations → a **named characterization** (below). See `hash/anf/`.
3. **Task 2b — the key (OSS CAD Suite)**: SymbiYosys `cover(success)` with bitwuzla
   synthesized an accepting input sequence (~12 s). See `key_search/`, `debug_plan.md`.
4. **Confirmation**: replayed the key through the reference sky130 simulation
   (`behavior_check/` harness) → `success=1`, `O = "(* TWO STARS *)"`.

## The chip's true purpose (task 2a — SOLVED: it is a Star Battle checker)

**The chip verifies a solution to a two-star Star Battle puzzle on an 11×11 grid.**
The 122-bit serial input is the grid, row-major, `1` = star (bit 122 is ignored). The
answer text `(* TWO STARS *)` is literally the puzzle's name, and the key is the puzzle's
**unique** solution. Full decode: `recon/opam/README.md`.

How each Star Battle rule is implemented in the 92 flops (all verified on the ground-truth
netlist model, `recon/opam/`):

| rule | hardware | evidence |
|---|---|---|
| position in the grid | 9-flop non-linear **122-state position counter** (proven by ANF brute force) | counter block, `recon/opam/reconstructed.v` |
| **exactly 2 stars per column** | 11 independent **2-bit saturating counters** (0/1/2/3+), each stepped only at positions `p ≡ c (mod 11)`; must read 2 | `automata.py`: no cross-pair mixing; 400/400 on perturbed grids |
| **exactly 2 stars per region** | 11 more 2-bit counters over 11 irregular position sets that partition the 121 cells — **the region map, read out of the silicon** | `starbattle.py`; map below |
| **exactly 2 stars per row** | 2-bit row counter `g__258,g__259` + sticky fail flag `g__254` | 400/400 |
| **no two stars touch** (incl. diagonal) | 12-stage input delay line (`I→g__186→…→g__231`) + sticky fail flag `g__205` tapping delays 1/10/11/12 = left, up-right, up, up-left neighbours | 400/400 |
| total stars = 22 | 8-bit ripple popcount `{g__215,g__201,g__224,g__393,g__236,g__233,g__190,g__183}` | literal readout |
| accept | `success' = (all of the above) & (g__180=1,g__243=0: 121 cells received) \| hold | Block 3 readout |

The region map (letters = regions; uppercase = the key's stars):

```
d d d d d j j A b B i
D d f d d J a a b b i
d d f j j j j A a B i
D d F j e e e i a a i
f d f j E i I i i i i
f f F j e e e i H h h
j j j j J j e i h k K
j C c c e e E i h k k
j c c G i i i i h k K
j j c g g I i i H h h
j C c G i i i i i i i
```

**Independent confirmation — one and only one solution.** `recon/opam/solve_starbattle.py`
solves this Star Battle from the region map alone (exhaustive backtracking, 16 s):
**exactly one solution, and it is the key.** For scale, 11×11 boards with 2 stars per
row/column and no touching number **31,197,434** when regions are ignored
(`count_noregion.py`); the hidden regions cut that to one. (A first, buggy solver produced
496 "candidates" that actually violate the region rule — fed to the netlist model only the
real key unlocked it; the chip caught the solver bug. Those 496 are *not* valid boards.)
So the key is *not* "one-way / only searchable" — it is the unique solution of a puzzle a
human can solve by hand.

How certain is "exactly one"? The column and region counters were decoded **exhaustively**
from the netlist (exact automata over every input position — no sampling), so those rules
are certain. The row-count flag (`g__254`) and the no-touch flag (`g__205`) were decoded by
**400/400 controlled perturbations** plus their structural support (row counter only /
input delay line only) — very high confidence, not a formal proof. Since bit 122 is a
don't-care, the chip accepts exactly one 121-cell board (two 122-bit strings).

The display sequencer prints the puzzle's feedback (all observed on the netlist model):

| grid | message |
|---|---|
| the unique solution | **`(* TWO STARS *)`** (`success=1`) |
| every row/column/region has 2 stars but two stars touch (`g__248`) | `TWO NOT TOUCH` |
| anything else | `TRY AGAIN` |
| no stars | `EMPTY SKY` |
| all stars | `BIG BANG` |

**Verification status (stated precisely):**
- **key on the reference sky130 cell models** — ✅ `success` high (and held) from cycle 125,
  `O` = `(* TWO STARS *)` (`recon/opam/tb_ref_sky130.v`, extracted netlist + sky130 UDPs).
  Shifting the key by ±1 cycle gives `TRY AGAIN` — replay alignment is the classic trap.
- **datapath (90 next-state functions) ≡ netlist** — ✅ **formally proven**, complete
  combinational SAT miter, `SAT proof finished - no model found: SUCCESS!`
  (`recon/opam/comb_miter.ys`, `comb_miter.log`; re-run 2026-08-15).
- **assembled RTL (`recon/opam/reconstructed.v`) ≡ netlist** — ✅ by **simulation**: `O` and
  `success` compared every cycle on key / wrong key / all-zero / 40 random runs → 0
  mismatches. ⚠️ The *sequential* whole-chip SEC (`recon/equiv_miter.ys`) did **not** complete
  (`build_miter.log` ends in an async-FF SAT error; needs `async2sync`) — so whole-chip
  equivalence is simulation-verified, not formally proven.
- **rules** — columns/regions exhaustive; rows/no-touch 400/400 perturbation; region map
  confirmed by the independent solver's unique solution == key; floorplan matches
  block-for-block.

*History note:* earlier drafts called this a "Galois NLFSR", then a "scrambled non-linear
hash lock". Both were overturned by the netlist: the "hash" is 22 independent 2-bit
counters (which is why BMC found the key in 12 s — there was never a one-way function).
Older write-ups in `hash/` and `hash/anf/` are kept as history and carry a superseded banner.

## Key gotchas that mattered

- **Protocol**: 3-cycle reset + 1 idle before enable; a wrong reset length gave
  garbage output. Decoded from the example VCD (which runs two failed attempts).
- **Replay alignment**: sby drives `PI_I <= key[cycle]` (non-blocking, effective
  next cycle) — the key needed a **+1 cycle offset** when replayed. This, not any
  model bug, was the whole blocker.
- **`success` self-holds** once fired (`success & (g__243 | ~g__180)`); an early decoder
  misread it as a pulse — read it after the last input bit, either way.

## Easter eggs spotted

- `example_inputs.vcd` header date `Dec 31 23:59:60 2016` — a real **leap second**.
- Version string: "Leave no stone unturned!"
- The answer itself is an **OCaml comment** `(* ... *)`.
- The display holds **five messages**, not two: `TWO NOT TOUCH` (counts right, stars touch), `EMPTY SKY` (all-zero input),
  `BIG BANG` (all-one input), `TRY AGAIN` (wrong key), `(* TWO STARS *)` (the key) —
  a sky theme (empty sky → big bang → two stars).
- The accept check embeds a **popcount checksum**: 22 ones = 2 stars × 11 rows.
- **The whole chip is a Star Battle puzzle**; the hidden 11×11 region layout is the real easter egg,
  and the answer `(* TWO STARS *)` names the puzzle type.

## Files

- `SOLUTION_key_bits.txt` — the 122-bit unlock key
- `debug_S1/full.v`, `full.vvp` — reference sim proving success + reading the answer
- `key_search/cover2.sby`, `key2.txt` — the BMC cover run + raw key
- `behavior_check/` — the golden-trace validation harness
- `hash/anf/` — exact per-bit update equations + the named characterization (task 2a)
- `hash/linearity/` — the non-linearity proof + per-flop linear/non-linear breakdown
- `hash/` — mechanism overview + the state dependency graph (superseded narrative, kept as history)
- `recon/opam/` — verified RTL, Star Battle decode, region map, independent solver, all testbenches
