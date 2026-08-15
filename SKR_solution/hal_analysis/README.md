# HAL Analysis (task 2a — circuit purpose)

Ran the recovered netlist through [HAL](https://github.com/emsec/hal) v4.5.0
(gate-level reverse-engineering framework) to characterize the puzzle's structure.

## Setup

```bash
HAL=~/Downloads/hal/build
export HAL_BASE_PATH=$HAL
export PYTHONPATH=$HAL/lib:$HAL/lib/hal_plugins        # hal_plugins needed for `import dataflow`
export LD_LIBRARY_PATH=$HAL/lib:~/Downloads/hal-local-deps/lib
python3 <script>.py <sky130.lib> <extracted_puzzle.v>
```

HAL builds the gate library directly from the sky130 liberty (`GateLibraryManager.load`)
via its liberty_parser plugin — no pre-built sky130 gate lib needed.

Scripts: `dana.py` (register grouping), `structure.py` (grouping + shift-chain check),
`trace.py` (success driver + I-influence).

## Netlist confirmation (3rd independent tool)

HAL parses `extracted_puzzle.v` and reports **gates=728, flip-flops=92**, inputs
`I, clk, enable, rst_n`, outputs `O[7:0], success` — matching both our KLayout-L2N
extraction and Magic. Three independent tools now agree on the netlist.

## Key structural findings

| finding | value | implication |
|---|---|---|
| `success` driver | a single `dfrtp_2.Q` (registered) | success is a 1-bit registered flag |
| success-register D cone | depends on **57 of 92** state FFs | final check is a combinational fn of 57 state bits |
| FFs whose data cone includes `I` | **58 of 92** | most of the state absorbs the serial input |
| direct FF.Q → FF.D chains | **0** | NOT a shift register (unlike the warmup) |
| DANA register groups | fragmented: max 6-bit (×3), 5-bit (×2), 38 singletons | no wide datapath / word structure |
| XOR + XNOR cells | 50 | feedback/mixing or comparison logic |
| mux2 cells | 21 | enable-gated state recirculation |

## Working hypothesis for the circuit's purpose

A **serial checksum / hash lock**, not a shift-and-compare:

- The serial input `I` is folded into a wide (~58-bit) state each enabled cycle,
  through XOR + AOI + enable-mux logic (no simple shift chain).
- `success` is a registered flag that goes high when a combinational function of
  57 state bits matches a hardcoded target — i.e. "does the accumulated state
  equal the expected value?"
- This matches an LFSR/CRC/MISR-style or custom-hash construction: fixed-length
  bitstream in, single accept bit out.

The design's heavy AOI/AND/OR content (577 comb cells vs only 50 XOR) suggests the
folding is **non-linear** (not a pure LFSR) — so the key is unlikely to be solvable
by linear algebra alone; a **SAT/BMC unrolling** (constrain `success=1`, solve for
the `I` sequence) is the indicated route for task 2b.

## Next HAL steps (available, not yet run)

- `solve_fsm` — if there's a control FSM among the small register groups.
- `sequential_symbolic_execution` / `netlist_simulator` — unroll the state update,
  drive toward `success=1` (the key search).
- `boolean_influence` — rank which `I`-cycles most influence `success`.
- `module_identification` — match known arithmetic/CRC structures.

---

## HAL white-box mechanism recovery (DANA + solve_fsm)

Ran HAL's structural tools to try to recover the mechanism (shift register? counter?
LFSR? control FSM?). Scripts: `../hash/fsm*.py`.

### DANA — register grouping
State is **fragmented**: largest groups are 6-bit (×3) and 5-bit (×2); the rest are
2-bit or singletons (38 one-bit groups). No clean wide datapath registers.

### solve_fsm — FSM extraction
Fix needed first: HAL's liberty-parsed gate library tagged the flop `D` pin as
`PinType.none`, so `solve_fsm` reported "0 data inputs". Patched the exported `.hgl`
(`next_state` pin → `data`, clear/preset → `reset`/`set`) — 38 pins fixed — then it ran.

Findings:
- **Every register group is entangled** with the rest of the state — even the most
  self-contained group reads **6 external flops**; others read 7–11. There is **no
  isolated FSM, counter, or shift register.**
- The most self-contained group (3 flops) solves to a small dense FSM: **8 reachable
  states, out-degree ~2**, with transitions conditioned on many external state bits
  (`net_98 & net_34 & …`). That is *not* a counter (which would be a linear chain) —
  it's a fragment of one big entangled state machine.

### Conclusion (mechanism)
The puzzle is a **deliberately scrambled hash/checksum lock**: the 92 flops form one
entangled accumulator (each next-state bit depends on the input and a wide slice of
the current state), and `success` is a registered equality-style check over 57 of
those bits. There is no recognizable sub-structure to read the purpose off of —
which is exactly why it resists white-box inspection and why the **black-box solver
route (BMC `cover(success)`) was the way in**, not mechanism recovery. On the warmup,
the same tools would have shown clean shift-registers + adder; here they show
scramble by design.

Remaining HAL method not yet run: `module_identification` (pattern-match known
arithmetic/known structures) and `boolean_influence` (rank input-cycle influence on
success).
