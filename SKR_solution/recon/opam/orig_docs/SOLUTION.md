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
success pulses high ~cycle 125; O reads "(* TWO STARS *)"
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

## The chip's true purpose (task 2a — solved and verified)

**The chip is a serial combination lock that reveals a hidden message.** It accepts exactly
one 122-bit key, is one-way by construction (so the key cannot be derived, only searched
for), and prints a message that depends on what it was fed. Stated with proven specifics:

- **It counts the input bits.** A closed, non-linear, **122-state saturating position
  counter** (9 flops, at the far-left of the die beside the input pins) tracks "which
  input bit is this"; it freezes after bit 122. Proven by brute-forcing the counter's
  own next-state ANF; 122 = the input length, confirmed independently from the example
  VCD.
- **It fingerprints the input two ways at once:**
  1. a **checksum on the number of 1-bits** — an 8-bit ripple counter of input ones
     (`{g__215,g__201,g__224,g__393,g__236,g__233,g__190,g__183}`) that must equal
     **22 = popcount(key)** (verified against the real key);
  2. a **non-linear hash of the bit *pattern*** — the input is absorbed into the state
     by *counter-addressed*, high-degree (≤13) non-linear mixing, and the check requires
     the resulting state to land on **26 specific bits = 1 and 30 specific bits = 0**
     (read out literally from the accept-check logic; see `recon/opam/README.md`).
- **It fires `success` exactly once**, on the cycle right after the 122nd input bit
  (`g__180=1, g__243=0`), then `g__243` latches "done" and the self-hold term
  `success & (g__243 | ~g__180)` keeps `success` high. So the accept check is a
  **pattern-match OR'd with a latch — not a pure `state == constant`**.
- **It selects a message from a 4-entry table** by `(success, popcount)`, formatted
  onto `O[7:0]` by a separate, provably-separable display sequencer:

  | input | popcount | message |
  |---|---|---|
  | the key | 22 | **`(* TWO STARS *)`** (`success=1`) |
  | any wrong key | any | `TRY AGAIN` |
  | all zeros | 0 | `EMPTY SKY` |
  | all ones | 121 | `BIG BANG` |

**Every one of these is verified**, by independent methods that agree:
- the datapath (90 flops) — **formal SAT-miter proof**, complete/unbounded, ≡ netlist;
- the whole assembled RTL incl. display + check — **end-to-end simulation ≡ netlist**
  on `O` and `success` every cycle (key, wrong-key, all-zero, 40 random runs → 0 mismatches);
- the accept condition — **literal readout** of the check logic, popcount=22 confirmed;
- the block decomposition — **physical floorplan** matches Jane Street's layout image
  block-for-block (`hash/floorplan_prediction_vs_actual.png`).

**That is the purpose: validate a 122-bit secret and unlock a message.** It is *not* a
named algorithm (CRC/LFSR/UART) — we ruled those out explicitly — and that is by design:
a lock's accept condition is meant to be an unrecognisable one-way function. The hash
*is* the fingerprint we read out; it was never meant to "mean" anything else.

*History note:* an earlier draft of this section called it a "Galois NLFSR with a 57-bit
equality comparator". Both parts were **overturned** by later work: the control block is a
counter (not an NLFSR/LFSR), and the check is a pattern-match with a latch (not an
equality comparator) — the netlist corrected the assumption. Full mechanism write-up in
`hash/README.md`, `hash/anf/`, `recon/opam/README.md`.

## Key gotchas that mattered

- **Protocol**: 3-cycle reset + 1 idle before enable; a wrong reset length gave
  garbage output. Decoded from the example VCD (which runs two failed attempts).
- **Replay alignment**: sby drives `PI_I <= key[cycle]` (non-blocking, effective
  next cycle) — the key needed a **+1 cycle offset** when replayed. This, not any
  model bug, was the whole blocker.
- **`success` is a pulse**, not a latch — check "ever high", not the final value.

## Easter eggs spotted

- `example_inputs.vcd` header date `Dec 31 23:59:60 2016` — a real **leap second**.
- Version string: "Leave no stone unturned!"
- The answer itself is an **OCaml comment** `(* ... *)`.
- The display holds **four messages**, not two: `EMPTY SKY` (all-zero input),
  `BIG BANG` (all-one input), `TRY AGAIN` (wrong key), `(* TWO STARS *)` (the key) —
  a cosmology theme (empty sky → big bang → two stars).
- The accept check embeds a **popcount checksum**: the key must contain exactly 22 ones.

## Files

- `SOLUTION_key_bits.txt` — the 122-bit unlock key
- `debug_S1/full.v`, `full.vvp` — reference sim proving success + reading the answer
- `key_search/cover2.sby`, `key2.txt` — the BMC cover run + raw key
- `behavior_check/` — the golden-trace validation harness
- `hash/anf/` — exact per-bit update equations + the named characterization (task 2a)
- `hash/linearity/` — the non-linearity proof + per-flop linear/non-linear breakdown
- `hash/` — mechanism overview + the state dependency graph
