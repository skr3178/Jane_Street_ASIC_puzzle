# Exact ANF — the literal update equations (the actual recurrence)

> **⚠ Superseded characterization.** The "Galois NLFSR + 57-bit equality comparator" headline
> below was the *first* reading of the ANF and was later **overturned** by the reconstruct-and-
> prove work: the control block is a **122-state position counter** (not an NLFSR/LFSR — the
> counter is non-linear, affine test failed), the datapath is **counter-addressed non-linear
> absorption**, and the check is a **56-literal pattern-match + latch incl. popcount=22** (not
> an equality comparator — `support=57` was insufficient, as cautioned). The equations and
> degree/monomial statistics below remain correct; only the *naming* was wrong. See
> `../README.md` ("Purpose, verified") and `../../recon/opam/README.md`.


We hold the netlist, so this isn't black-box: `anf_extract.py` computes the exact
**algebraic normal form** (XOR-of-ANDs over GF(2)) of every flip-flop's next-state
function, using the sky130 Liberty cell functions and symbolic GF(2) propagation
(pure stdlib). Outputs: `anf_report.md` (per-flop degree/monomials) and
`anf_equations.txt` (the literal equation of each flop).

## Named characterization

**A 92-bit Galois-configuration non-linear feedback shift register (NLFSR) with
non-linear (gated) input absorption and a 57-bit equality-comparator accept check.**

Evidence from the equations:

| property | value | meaning |
|---|---|---|
| Galois self-feedback `Q_i' = Q_i ⊕ (…)` | **86 / 92** bits | Galois configuration (each bit has its own feedback), not Fibonacci (one chain + one feedback) |
| input enters **linearly** (`… ⊕ I`) | **0** bits | the input is *never* just XORed in |
| input enters **non-linearly** (`I & Q_a & Q_b …`) | **58** bits | serial input is **gated into products of state bits** — non-linear absorption, not sponge injection |
| algebraic degree, hash core (51 bits) | 4–13, **mean 10.2** | very high degree → strong non-linear mixing, one-way |
| algebraic degree, display (39 bits) | 2–10, mean 5.9 | high logic degree, but affine on restricted (low-weight) reachable states |
| accept check `g__197` (=`success`) | ANF blows up, **support = 57** | a **57-bit equality comparator** — matches the success cone exactly |
| second check `g__248` | blows up, support = 57 | a second 57-bit comparison bit |
| `clk` in any support | 0 | clean extraction (cross-check) |

## What each core-bit equation looks like

```
g__179' = g__179 ⊕ I·enable·g__179·g__180·g__181·g__187·g__199·g__214·g__221·g__237·g__245·g__250 ⊕ …
```
i.e. **hold the bit, then XOR in an input-gated product of ~10 other state bits.**
Every one of the 58 input-touching bits mixes `I` inside such products — the serial
key bit modulates high-degree state products each cycle. Degrees run to 13 (a monomial
multiplying 13 state variables), so this is far past a quadratic NLFSR — it's deep
non-linear feedback, cryptographic-register-class mixing.

## Reconciliation with the simulation linearity test

The sim (`../linearity/`) found 41 bits "linear" — on the **reachable** state space.
The ANF shows those same bits have **high-degree logic** (mean degree 5.9). No
contradiction: the display bits run at **low Hamming weight** (2–3 of 6 set,
verified), so their high-degree product terms mostly vanish on reachable states and
they behave affinely. ANF = degree of the *logic*; sim = behavior on *reachable
states*. Both correct, measuring different things. The `g__197` support = 57
cross-check also confirms the ANF against the independent cone analysis.

## Bottom line

The "true purpose", as concretely as it admits:

> The chip is a **92-bit Galois NLFSR** clocked once per input bit. The serial input
> is **absorbed non-linearly** (gated into products of state bits), driving the state
> through a **high-degree (≤13)** one-way mixing. After the 122-bit key, a **57-bit
> equality comparator** (`success`) fires iff the state hit its hidden target;
> unlocking flips the output ROM from "TRY AGAIN" to `(* TWO STARS *)`. A separate
> low-weight sequencer drives the ASCII output. Because the absorption is high-degree
> non-linear, the key is not algebraically invertible — only searchable (BMC), which
> is how it was found.

## Files

- `anf_extract.py` — the extractor (pure stdlib; netlist + Liberty → ANF)
- `anf_equations.txt` — the literal update equation of all 92 flops
- `anf_report.md` — per-flop table: support, algebraic degree, #monomials
