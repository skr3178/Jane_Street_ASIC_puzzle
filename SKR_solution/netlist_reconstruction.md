# Netlist reconstruction — determining function definitively

## The core principle

"Definitive" in netlist reverse engineering means **proof, not inspection**. Reading gates,
drawing schematics, and simulating are all hypothesis *generation*. The only way to
definitively establish function is hypothesis *confirmation* by an exhaustive or formal
method. So the reliable workflow is a loop:

**recover structure → form a hypothesis → prove or refute it formally**

What makes this better than plain iteration is that the refutation step hands you a
counterexample, so every failed guess tells you exactly where your model is wrong — the
loop converges instead of wandering.

---

## Step 1 — Normalize, don't read raw gates

A post-synthesis netlist is bit-blasted and optimized; the human-meaningful structure is
gone at the gate level. First move it into a tool (yosys/ABC) with the cell library's
logic functions loaded, clean it, and optionally resynthesize to a simpler gate set.
You're not trying to understand it yet — you're getting it into a form where algorithms
can operate on it. Any transform you apply should itself be equivalence-checked so you
never analyze a corrupted copy.

## Step 2 — Recover the architecture from the state, not the logic

The combinational gates are the least informative part. The **flip-flops are the
skeleton**: group them into registers and the design's architecture falls out.

- Flops chained Q→D form a **shift register**; with XOR feedback taps, an **LFSR**; with
  an incrementer in the feedback path, a **counter**; a small cluster with dense
  cross-coupling and one-hot or binary encoding is an **FSM state register**.
- Shared enables, shared muxes, and parallel identical logic slices reveal **word-level
  buses** that bit-blasting destroyed.
- Tools automate this: HAL's dataflow analysis (DANA) groups flops into candidate
  registers; yosys can render fan-in cones per register so you see each register's update
  function in isolation.

Once you know "this is an 8-bit counter, this is a 24-bit shift register, this is a 3-bit
FSM," the function is nearly written for you — the registers plus their update rules *are*
the behavior.

## Step 3 — Canonical forms for combinational cones

For each output or register D-input, extract its fan-in cone. If the cone's support is
small (≲16–20 inputs), you can be definitive immediately:

- **Truth table by exhaustion** — definitive by construction.
- **BDDs** — canonical: two functions are equal iff their BDDs are identical, so matching
  a cone against a candidate (comparator, adder bit, parity) is an equality test, not a
  judgment call.
- Structural matchers (e.g. full-adder extraction, known-subcircuit matching) flag
  arithmetic definitively at the cell-pattern level.

## Step 4 — Interrogate with SAT/BMC instead of staring

Replace "what does this do?" with decidable questions a solver answers with proof or
counterexample:

- "Can this output ever go high?" / "What input sequence makes it go high?" — bounded
  model checking will *synthesize the answer input* for you. For lock/checker-style
  circuits this is the shortcut: you learn the function by making the solver satisfy it.
- "Are these two registers always equal?" / "Is this signal constant?" — kills or confirms
  structural hypotheses instantly.
- If the state register is small, SAT-based reachability enumerates the actual state
  graph — and a state graph is the complete, definitive description of an FSM.

## Step 5 — The definitive endpoint: reference model + equivalence proof

Write clean RTL expressing your hypothesized behavior and prove it equivalent to the
netlist (miter + SAT for combinational; BMC plus temporal induction, or tools like EQY,
for sequential).

- **PASS** = definitive, unconditionally: the netlist implements your RTL for every input,
  every cycle. You now have not just an understanding but a readable specification with a
  machine-checked proof attached.
- **FAIL** = a concrete counterexample trace showing the first cycle where your model
  diverges — the highest-quality debugging signal you can get.

Sequential caveats: match reset behavior, and remember the netlist's state encoding may
differ from your model's — induction over reachable states (or adding register mappings)
handles that.

## Where simulation fits

Dynamic simulation is the cheapest hypothesis generator — drive stimulus, watch the
grouped registers in a waveform viewer, guess the mechanism. Just never mistake it for the
conclusion: it's definitive only when you've exhausted the input space, which essentially
never happens for sequential logic.

**The hierarchy of certainty**, top to bottom:

1. Formal equivalence vs. a reference model
2. BDD / truth-table canonical comparison per cone
3. SAT/BMC answers to specific properties
4. Structural pattern matching
5. Simulation
6. Eyeballing the schematic

Work upward from the bottom to form guesses; only the top two let you say "this netlist
computes X" and mean it as a theorem.

---

# Tools for each step

Almost all of this is open source, and most of it is already installed on this machine.

## Ingest & normalize

- **Yosys** — the workhorse. `read_verilog` + `read_liberty` to load the netlist with real
  cell functions, `flatten`/`opt_clean` to normalize, `techmap`/`aigmap`/`abc` to
  resynthesize into a simpler gate set, `write_json` to get a machine-readable graph for
  your own scripts.
- **ABC** (bundled inside yosys, also standalone) — AIG-level optimization and rewriting;
  often makes an obfuscated-looking cone collapse into something recognizable.

## Register grouping & structural exploration

- **HAL** (TU Darmstadt / Ruhr-Bochum) — purpose-built netlist reverse-engineering
  framework. Its **DANA** plugin does automatic register grouping from a sea of flops; the
  GUI lets you trace nets interactively; the Python API (`hal_py`) lets you script graph
  queries (fan-in cones, shared-enable clustering, isolating subcircuits into modules).
- **Yosys `show` / netlistsvg** — render selected cones as schematics; `select -set` +
  `show` on one register's fan-in at a time is far more useful than plotting the whole
  design.
- **Python + networkx** over yosys's JSON export when you want custom graph analysis
  (dominators, SCCs, cut points).

## Canonical cone analysis

- **ABC `collapse` / truth-table printing** — exhaustive characterization of small cones;
  BDD-based, so equality against a candidate function is a canonical-form comparison, not
  a heuristic.
- **Yosys `eval` and `sat`** — evaluate a cone under chosen constants, or ask "does this
  cone equal this expression" directly.
- **Yosys `extract_fa`** — pattern-matches full/half adders, which is how you spot
  arithmetic datapaths in a bit-blasted netlist; the generic `extract` command matches any
  subcircuit you provide against the design.

## Property queries, BMC, state-graph recovery

- **SymbiYosys (`sby`)** — the front-end for BMC and k-induction. The killer feature for a
  checker-style circuit is `cover()`: write `cover(success)` and the solver *synthesizes
  the input sequence* that fires it.
- **`write_smt2` + yosys-smtbmc** with a solver (**Bitwuzla/Boolector** are fastest for
  bit-vector hardware problems; Z3/Yices as alternates) — for longer traces or custom
  reachability scripts.
- **Yosys `sat`** with `-seq N` for quick bounded sequential queries without leaving
  yosys.
- **HAL's FSM-solver plugin** — given the state register and inputs, extracts the actual
  state-transition graph via SAT, which is the definitive FSM description.

## Equivalence proving (the definitive step)

- **EQY** — yosys's equivalence-checking front-end; partitions the design and proves
  gold ≡ gate per partition, works well for RTL-vs-netlist.
- **Yosys `miter` + `sat -prove`**, or the `equiv_make`/`equiv_induct` flow — the manual
  route when you want control over matching points.
- **ABC `cec`** — very fast combinational equivalence at the AIG level.
- Commercial equivalents (Cadence Conformal, Synopsys Formality, JasperGold for
  properties) are the industry standard but nothing here needs them.

## Hypothesis-testing simulation

- **Icarus Verilog / Verilator + GTKWave** — drive stimulus and watch the *grouped
  registers* (not raw nets) to guess mechanisms cheaply.
- **cocotb** — Python testbenches, convenient when your stimulus or output decoding
  (e.g., ASCII streams) is easier to express in Python than Verilog.

## Local environment notes

The stack is essentially complete here already: yosys/eqy/sby via the librelane nix shell,
iverilog/verilator/gtkwave native from OSS CAD Suite, and HAL built with all plugins
(DANA and the FSM solver included). The one gap worth closing if you script SMT queries
directly is making sure a fast bit-vector solver like Bitwuzla is on PATH — OSS CAD Suite
ships one.
