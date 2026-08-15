# recon/opam/ — O-cone splice, accept-check readout & verification of reconstructed.v (modified copy here; ../reconstructed.v is the original)

`reconstructed.v` — readable RTL that is behaviourally identical to the recovered netlist
(`puzzle_behav.v`, the yosys-lowered ground truth of `extract/puzzle/extracted_puzzle.v`).

| block | content | evidence |
|---|---|---|
| 1 | 9-bit non-linear saturating position counter (122 states) | ANF; combinational SAT miter (`../GOLD.v`/`../GATE.v`, `comb_miter.ys` → `comb_miter.log`: SUCCESS) |
| 2 | counter-addressed non-linear absorption of `I` into the state | same miter: all 90 datapath next-state fns ≡ netlist |
| 3 | accept check = 56-literal pattern match, self-holding | literal readout below; `o_lower.py`-style walk of the cone |
| 4 | O output cone: 161 cells lowered 1:1 from the netlist (`o_lower.py` → `o_cone.vinc`) | `tb_diff.v` |

## Verification of the finished file
`tb_diff.v` drives `puzzle` (ground truth) and `puzzle_reconstructed` side by side and compares
`O` and `success` every cycle: key run, LSB-first key run, all-zero run, 40 random 300-cycle runs
→ **TOTAL MISMATCHES = 0**.

```
cd SKR_solution && iverilog -g2012 -o /tmp/tb_diff.vvp recon/opam/tb_diff.v recon/puzzle_behav.v recon/opam/reconstructed.v && vvp /tmp/tb_diff.vvp
```

## Accept-check readout (the "hidden fingerprint")
`success' = MATCH | (success & (g__243 | ~g__180))`, `MATCH` = AND of 56 literals:
- must be 1: g__180 g__190 g__192 g__194 g__195 g__198 g__202 g__203 g__207 g__210 g__213 g__214 g__216 g__217 g__222 g__225 g__226 g__228 g__229 g__233 g__241 g__242 g__249 g__260 g__262 g__393
- must be 0: g__179 g__182 g__183 g__184 g__188 g__189 g__193 g__200 g__201 g__204 g__205 g__211 g__215 g__218 g__219 g__224 g__230 g__232 g__234 g__235 g__236 g__238 g__243 g__244 g__252 g__253 g__254 g__257 g__261 g__263

Semantics recovered from the literals:
- `g__180=1, g__243=0` — the one cycle right after the 122nd input bit (the check fires once; `g__243` then latches "done" and holds `success`).
- `{g__215,g__201,g__224,g__393,g__236,g__233,g__190,g__183} (MSB..LSB)` is an **8-bit ripple counter of input ones** (each bit toggles on `I&enable&~g__180&<all lower bits>`); the match requires it to be **22 = popcount(key)** — confirmed in simulation (`cnt=22`).
- 22 datapath bit-pairs must read `(a=0, b=1)`, plus `g__254=0`, `g__205=0`.
- `chk_248` (flop `g__248`) is the *same* match with `g__205=1` — a sibling latch that was never seen firing.

## Output generator (readable meaning of Block 4)
When `g__243=1` (done), a 4-bit character index `{g__539,g__11,g__10,g__9}` steps through a message chosen by
(`success`, popcount counter, data register `{g__405,g__206,g__13,g__208,g__227,g__14,g__256,g__12}` — an 8-bit
scrambler that shifts every cycle):

| input | popcount | text |
|---|---|---|
| the key | 22 | `(* TWO STARS *)` (`success=1`) |
| anything else tried (key with a bit flipped, key LSB-first, random) | any | `TRY AGAIN` |
| all zeros | 0 | `EMPTY SKY` |
| all ones | 121 (ones are counted while `~g__180`, i.e. cycles 4..124) | `BIG BANG` |

Extra input after the 122 bits, or dropping `enable` after the key, does not disturb the result.

Helper scripts: `netparse.py` (netlist+Liberty parser split from `hash/anf/anf_extract.py`),
`o_eval.py`/`o_probe2.py` (O-cone probing), `o_lower.py` (cone → Verilog), `tb_trace.v`, `tb_var.v`.

---

## THE TRUE PURPOSE — it is a Star Battle checker (`starbattle.py`, `automata.py`, `solve_starbattle.py`)

The "non-linear hash" framing was wrong. Enumerating the 22 accept-check pairs (`automata.py`) shows each pair is an
**independent 2-bit saturating counter (0/1/2/3+) of the input ones it sees**, stepped only at counter-selected input
positions — no cross-pair mixing at all (that is also why BMC found the "preimage" in 12 s). Success needs every
counter to read exactly **2**. The watched position sets are:

- 11 sets `p ≡ r (mod 11)` → the **columns of an 11×11 grid** (input is the grid, row-major, 1 = star);
- 11 irregular sets partitioning the 121 cells → the **regions** of the puzzle (map below).

The remaining flags decode the other Star Battle rules (verified 400/400 on perturbed grids, `tb_moves.v`):

| flop(s) | meaning |
|---|---|
| 22 pairs | each column and each region contains exactly 2 stars |
| `g__254` (+ `g__258,g__259` row counter) | sticky: some row does not contain exactly 2 stars |
| `g__205` (+ 12-stage input delay line `I→g__186→g__209→g__247→g__220→g__196→g__223→g__178→g__212→g__185→g__255→g__240→g__231`; the flag taps delays 1, 10, 11, 12 = left / up-right / up / up-left neighbours, with counter bits to mask row edges) | sticky: two stars touch (incl. diagonally) |
| 8-bit popcount = 22 | total stars = 2 × 11 |
| `g__180=1, g__243=0` | all 121 cells received (bit 122 is ignored) |

**Region map recovered from the silicon** (letters = regions, uppercase = the key's stars):
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
`solve_starbattle.py` solves this 2★ Star Battle independently (exhaustive backtracking, 16 s): **one and only one
solution, and it equals the key** — so the key is not "only searchable": it is the unique solution of a hand-solvable
puzzle. (Without regions, 31,197,434 boards satisfy rows/columns/no-touch — `count_noregion.py`.) The board is 121 cells;
the chip ignores the 122nd input bit, so exactly one board (two 122-bit strings) is accepted.

**Certainty:** columns/regions are decoded exhaustively (exact automata, every position); the row flag `g__254` and the
touch flag `g__205` are decoded by 400/400 perturbations + structural support — high confidence, not a formal proof.

**Proof status (precise):** key confirmed on the **sky130 reference-cell netlist** (`tb_ref_sky130.v`: success held from
cycle 125, `(* TWO STARS *)`; ±1-cycle misalignment → `TRY AGAIN`). Datapath ≡ netlist **formally** (`comb_miter.ys`,
complete combinational SAT, SUCCESS). Assembled RTL ≡ netlist **by simulation** (`tb_diff.v`, 0 mismatches); the
sequential whole-chip SEC in `../equiv_miter.ys` did **not** complete (`../build_miter.log`: async-FF SAT error).

The output messages are the puzzle's feedback (all seen on the ground-truth model):

| grid | message |
|---|---|
| the unique solution | `(* TWO STARS *)` — the puzzle's name, in an OCaml comment |
| all counts right but two stars touch (`g__248`) | `TWO NOT TOUCH` |
| anything else | `TRY AGAIN` |
| no stars | `EMPTY SKY` |
| all stars | `BIG BANG` |

Files: `automata.py` (pair enumeration), `starbattle.py` (grid/region readout), `solve_starbattle.py` (independent solver),
`tb_sols.v`/`tb_sols2.v`/`sols.mem` (496 candidates from a buggy first solver — they violate the region rule and are NOT valid boards; chip accepted only the key, which
exposed the solver bug), `tb_moves.v`/`moves.mem`/`moves.props` (flag decoding), `tb_touch.v`/`touch.mem`.

## Figures (generated here)
| file | shows |
|---|---|
| `starbattle.png` | recovered regions + the unique solution |
| `waveform_key_vs_wrong.png` | reference-cell sim traces: key vs one-star-moved board (`tb_wave.v`, `wave_*.csv`) |
| `block_diagram.png` (`.dot`) | architecture: counter → 22 rule counters + row/touch/popcount → AND → success → messages |
| `rule_counter_automaton.png` (`.dot`) | the 0/1/2/3+ saturating counter each column/region pair implements |
| `rule_silicon_map.png` (`rule_silicon_map.py`, `placement.json` from `placement_dump.py`) | every std cell of the real placement coloured by rule; the bottom-right block = region address decoder |
| `messages.png` | the five output messages with a triggering board each |
