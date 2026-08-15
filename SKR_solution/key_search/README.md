# Key search (task 2b) — status & findings

Goal: find the `I` bit-sequence that drives `success` high, using OSS CAD Suite
(yosys/sby/smtbmc + bitwuzla). Then read the answer string off `O`.

## What works (validated)

- **OSS CAD Suite ready**: yosys 0.68, sby 0.68, smtbmc, solvers bitwuzla 0.9.1 /
  boolector / yices / z3, all on PATH via `source ~/oss-cad-suite/environment`.
- **Behavioral validation of the netlist** (see `../behavior_check/`): simulating
  `extracted_puzzle.v` with the reference sky130 cell models and the exact
  `example_inputs.vcd` waveform reproduces `O = "TRY AGAIN"` ×2, `success=0` —
  EXACT match to Jane Street's trace. The netlist is behaviorally correct.
- **cover(success) is tractable**: bitwuzla reaches `success` in ~12 s.
  Formal model built with `read_liberty -wb` + `flatten -wb` + `prep`.

## The real operating protocol (decoded from example_inputs.vcd)

```
cycles 0–2 : rst_n=0, enable=0    (reset held 3 cycles)
cycle  3   : rst_n=1, enable=0    (reset released, 1 idle cycle)
cycle  4+  : rst_n=1, enable=1    (input processed, 1 bit/cycle)
rst_n low again at 156–158        (example runs TWO attempts → "TRY AGAIN" ×2)
242 active (rst_n & enable) input cycles total across the two attempts
```
`success` is a registered flag; its cone = 79 of 92 FFs. The 4 un-reset `dfxtp`
flops are NOT in the success cone (so `success` is init-independent), but they ARE
in the `O` cone.

## RESOLVED (2026-08-15) — it was replay alignment, not a model discrepancy

> The key **does** unlock the sky130 reference-cell netlist: 3-cycle reset, 1 idle cycle,
> then the 122-bit key MSB-first from cycle 4 → `success` high from cycle 125 (and held),
> `O` = `(* TWO STARS *)`. Shifting the key by ±1 cycle gives `TRY AGAIN`, which is exactly
> what the failed replays below saw (cause 2). Reproduce: `recon/opam/tb_ref_sky130.v`.
> The rest of this section is kept as history.

## (historical) OPEN ISSUE — yosys `-wb` model ≠ reference cells

- Harness `harness2.sv` reproduces the real protocol (rst_n/enable from a cycle
  counter). `cover(success)` on the yosys `-wb` model → **PASS at step 127**; the
  solver emits a 127-cycle `I` key (`key2.txt`).
- Replaying that key through the **reference sky130 sim** (validated above):
  - correct-protocol driver (`reftb3.v`)  → `success=0`, `O="TRY AGAIN"`
  - exact sby-timing replay (`ref_exact.v`) → `success=0`, `O` garbage `.(* `
- So the key the BMC found does **not** satisfy the reference model. Two candidate
  causes, not yet disambiguated:
  1. **Model discrepancy**: yosys `read_liberty -wb` models the async **set**
     flops (`dfstp_2`, 4 of them) and/or async-reset flops differently from the
     sky130 reference UDPs (e.g. set-to-1 vs reset-to-0, or set/reset priority).
     If any dfstp is in the success cone, the BMC solves a different circuit.
  2. **Replay alignment**: off-by-one between sby's non-blocking `PI_I <= key[c]`
     indexing and the reference driver's sampling.

  The "exact sby-timing" replay giving *garbage* O (vs the clean "TRY AGAIN" from
  the hand-built driver) points at cause 1 (the two models genuinely diverge),
  since identical stimulus yields different O.

## Next steps to resolve

1. **Prove or refute the model discrepancy**: equivalence-check the yosys `-wb`
   representation of `puzzle` against a reference-cell representation (or just the
   4 dfstp/dfrtp flop models) — miter + `sat`, or compare truth tables of the
   flop `-wb` models vs the sky130 UDPs. If they differ, that's the bug.
2. **Do the key search on a reference-faithful model**: either
   (a) build the formal model from the sky130 **functional Verilog** (blackbox the
       cells with correct behavioral models) instead of `-wb` liberty, or
   (b) fix the flop models so `-wb` matches the reference, then re-run cover.
3. Once a key passes the **reference** sim (success=1), read `O` there — that ASCII
   string (replacing "TRY AGAIN") is the final answer.

## Files

- `harness2.sv` — correct-protocol formal wrapper (rst_n/enable from counter)
- `cover2.sby` — sby cover(success) config, depth 320, bitwuzla
- `key2.txt` — the 127-cycle I sequence the BMC found (NOT yet reference-valid)
- `reftb3.v`, `ref_exact.v` — reference-cell replay attempts (both failed on alignment; resolved, see above)
- `harness.sv`, `cover300.sby`, `key_from_tb.txt` — earlier WRONG-protocol attempt
  (enable=1 always, 1-cycle reset); superseded, kept for reference
