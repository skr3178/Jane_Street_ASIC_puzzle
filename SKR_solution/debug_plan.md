# Minimal stepwise debug plan — task 2b (key search)

## The blocker  *(resolved — replay alignment; the key unlocks the sky130 reference netlist, see `recon/opam/tb_ref_sky130.v`)*

`cover(success)` on the yosys `read_liberty -wb` model finds a 127-cycle key, but
that key **fails the reference sky130 sim** (success=0, O="TRY AGAIN"). So the
`-wb` formal model and the reference cell models disagree. Prime suspect: the async
**set** flops `dfstp_2` (4 in the puzzle) — never exercised by the warmup EQY
(warmup has only `dfrtp` reset flops), so `-wb`'s `dfstp` model is unvalidated.

## The oracle (what makes this debuggable)

`example_inputs.vcd` is a **known input → known output** pair, per model:

| | value |
|---|---|
| cycles | 312, two attempts (reset at 156) |
| per attempt | **121 active input bits** (rst_n=1 & enable=1) |
| attempt-1 I bits | `0010101000000010110000101001100000000010000001110110000100101100001110011000000010110000001011100000000010000011001110000` |
| attempt-2 I bits | `1101011000010011110000000001000001000011000011101110000100001100001001011000000101110000110011100000000010000000000100000` |
| expected O | "TRY AGAIN" (both attempts) |
| expected success | 0 (both) |

**Rule: "a model is wrong" = it does not turn attempt-1's 121 bits into "TRY AGAIN".**
Reference cells already pass this (see `behavior_check/`). Everything below tests
each candidate model against this oracle.

## Steps (each gated by the oracle; stop at first failure and fix there)

- **S0 — baseline (DONE):** reference sky130 sim reproduces "TRY AGAIN" ×2,
  success=0 on the full example. ✅ (`behavior_check/`)

- **S1 — does the `-wb` model pass the oracle?**
  Feed attempt-1's 121 bits (correct protocol: 3 rst cycles, 1 idle, then enable=1)
  into the yosys `-wb` model (via `yosys sim`, or smtbmc replay), decode O.
  - O == "TRY AGAIN"  → `-wb` model is behaviorally fine; the bug is in the key
    **replay/alignment**, not the model → go to S4.
  - O != "TRY AGAIN"  → `-wb` model diverges from reference → go to S2.

- **S2 — localize the divergent cell(s).**
  - Are the 4 `dfstp_2` in the `success` cone? in the `O` cone? (`yosys select`)
  - One-flop miter: build `dfstp_2` from `-wb` liberty vs the sky130 reference UDP,
    drive CLK/D/SET_B, compare Q (post-reset value, set polarity, set/reset
    priority). Same for `dfrtp_2`, `dfxtp_2` if needed.
  - Expected finding: `-wb` `dfstp` powers/reset to the wrong value (0 vs 1) or
    ignores SET_B.

- **S3 — fix the flop model, re-verify against the oracle.**
  Keep `-wb` for combinational cells (proven correct by warmup EQY). Replace only
  the flops with reference-faithful models — either:
  (a) hand-written behavioral `dfrtp_2`/`dfstp_2`/`dfxtp_2`, or
  (b) map flops to generic `$_DFF_*` with correct set/reset via `dfflegalize`.
  Then re-run S1: the fixed model MUST reproduce "TRY AGAIN" on attempt-1.

- **S4 — re-run `cover(success)`** on the oracle-passing model → extract key.

- **S5 — validate the key in the reference sim.**
  Replay through `behavior_check`-style reference sim. success must go high.
  If not, the residual is replay **alignment** (off-by-one in cycle→I mapping) —
  fix by matching sby's non-blocking `PI_I <= key[c]` timing exactly.

- **S6 — read the answer.**
  With success=1 in the reference sim, decode `O`: the ASCII it emits (instead of
  "TRY AGAIN") is the final answer string.

## Sanity checks available at every step (no reference needed)

- attempt length is 121 bits — a key wildly off this length is suspect.
- success cone = 79 FFs; the 4 `dfxtp` are NOT in it (so success is init-independent
  — a key that depends on power-up state is wrong).
- O is deterministic under the correct protocol (garbage O = wrong protocol/init).

## Artifacts

- oracle: `../example_inputs.vcd`; reference baseline: `behavior_check/`
- current (superseded) key attempts: `key_search/` (`cover2.sby`, `key2.txt`, `reftb3.v`)
