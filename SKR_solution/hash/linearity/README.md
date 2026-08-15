> **SUPERSEDED (2026-08-15).** The "one-way hash" reading below was overturned: the accept check is
> 22 *independent* 2-bit counters + two flags — **the chip is a two-star Star Battle checker on an
> 11×11 grid** with one and only one solution (== the key). See `../../recon/opam/README.md` and
> `../../SOLUTION.md`. This file is kept as history of how the analysis got there.

# Linearity test — is the hash linear (CRC/LFSR) or non-linear?

**Verdict: NON-LINEAR.** The state-fold is a genuine non-linear hash, not an
LFSR/CRC. It is therefore not algebraically invertible — the unlock key can only be
found by search (which is exactly why BMC `cover(success)` was the way in).

## Method

Treat the chip as a function `F(X)` = the 92-bit state after shifting in a 122-bit
input `X` under the real protocol (3-cycle reset, 1 idle, enable, then the bits).
`F` is affine (linear) iff, for random inputs,

```
F(X1) ⊕ F(X2) ⊕ F(X1⊕X2) ⊕ F(0) = 0     (the affine constant F(0) cancels)
```

Implementation (`linearity/`):
- `puzzle_probe.v` — the netlist instrumented with `output [91:0] STATE` = the
  concatenation of all 92 flip-flop Q nets (so the internal state is observable).
- `tb.v` — applies the protocol, reads a 122-bit input from `input.mem`, prints STATE.
- driven by a Python script over 30 random input pairs (iverilog + sky130 ref models).

## Result

- **30 / 30 trials non-zero** → non-linear.
- **51 of 92 state bits** are non-linear; ~41 are linear → a linear skeleton with a
  heavy non-linear mixing core.
- ~40 bits flip per superposition test → strong non-linearity (not a few stray taps).
- `F(0)` had no X bits — all 92 flops resolve to defined values under the protocol,
  so no masking was needed and the test is exact/deterministic.

## Consequence for "true purpose"

The chip is a **serial non-linear hash lock**: input folded into 92-bit state via
non-linear mixing; `success` when a 57-bit slice == hidden target. Non-linear ⇒ no
matrix/polynomial, no algebraic inverse ⇒ key only findable by search. This *proves*
(not assumes) why the solver route was necessary. Remaining extractable property: the
57-bit target constant (SAT on the `$4240` check).

## Per-bit breakdown (`per_bit_report.md`)

The 51 non-linear / 41 linear split maps almost perfectly onto **function**:

| group | flops | non-linear | linear |
|---|---|---|---|
| hash core (success cone) | 57 | 51 | 6 |
| output-generator only | 35 | **0** | 35 |

So the chip is a **non-linear hash core (57-bit) + a purely linear output formatter
(35-bit)**. The one-wayness is concentrated exactly in the checked state; the display
path is linear (it just routes state → ASCII). All 51 non-linear bits are `dfrtp_2`;
the 4 `dfstp_2` and 4 `dfxtp_2` are linear. Full 92-row table in `per_bit_report.md`.

## Closure check — is the linear part a self-contained subsystem?

Tested whether the linear flops ever read a non-linear flop (they shouldn't — reading
a non-linear bit would make them non-linear too). Result:

- **38 of 41 linear flops are fully closed** — driven only by input + other linear
  flops, never by the hash core. This is the **independent linear display subsystem**.
- The **3 exceptions are `g__197` (the `success` register), `g__248`, `g__215`** —
  they *do* read the non-linear core, and are **constant 0 on random inputs**
  (verified over 25 random probes). They only tested "linear" because a constant is
  trivially affine — the known blind spot of random-probe linearity testing. They are
  really the **check/success machinery** (active only at the key), not linear.

So there are **no true violations**: every flop that reads the hash core is either
non-linear or a constant-on-random check bit. Refined architecture:

| block | flops | nature |
|---|---|---|
| non-linear hash core | 51 | the one-way lock |
| check / `success` machinery | 3 | reads the core; constant-0 until the key hits |
| **closed linear display subsystem** | **38** | provably independent of the hash |

This cross-validates the linearity test: the *only* "linear" flops touching the core
are exactly the constant-on-random ones, as theory predicts.
