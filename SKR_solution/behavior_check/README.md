# Behavioral validation — netlist vs Jane Street's ground-truth I/O

The strongest validation available for the puzzle (there is no gold netlist, but
there **is** a gold I/O trace): simulate `extracted_puzzle.v` with the exact inputs
from `example_inputs.vcd` and confirm it reproduces the known outputs.

## Result — PASS

```
input:   the 242-bit I stream + clk/rst_n/enable waveform from example_inputs.vcd
output:  O = ".TRY AGAIN.TRY AGAIN."   (. = <0> null between words)
         success = 0
expected (Jane Street's VCD): "TRY AGAIN" x2, success = 0   ✓ EXACT MATCH
```

Our recovered netlist is not just structurally sound (warmup EQY, yosys check,
KLayout/Magic/HAL agreement) — it is **behaviorally identical** to the real chip on
the one stimulus we can check, including the output-generator region that produces
the ASCII string.

## How it was run

```bash
source ~/oss-cad-suite/environment
V=~/.ciel/ciel/sky130/versions/8afc8346*/sky130A/libs.ref/sky130_fd_sc_hd/verilog
iverilog -g2012 -DUNIT_DELAY='#1' -o sim.vvp \
    tb.v ../extract/puzzle/extracted_puzzle.v $V/primitives.v $V/sky130_fd_sc_hd.v
vvp sim.vvp        # → sim_out.vcd
```

Key points:
- **No `USE_POWER_PINS`**: the sky130 behavioral models then have no power pins,
  matching our power-less netlist instantiations exactly.
- `tb.v` replays the *exact* input event stream (times + values) parsed from
  `example_inputs.vcd`, so timing matches the reference bit-for-bit.
- `sim_out.vcd` is decoded the same way as the input VCD; O transitions spell the
  ASCII, success is read at the end.

## Why this matters for task 2

This validated simulation harness is the foundation for the key search (task 2b):
we can now drive the netlist with confidence that "success goes high" in *our*
model means the same thing on the real chip. Same reset/enable protocol, same
clocking. The next step feeds free inputs and asks a solver (`cover(success)` via
SymbiYosys) to synthesize the input sequence that flips success to 1.

Files: `tb.v` (generated testbench), `puzzle_sim.v` (yosys whitebox model, unused
in the final iverilog flow), `sim.vvp`, `sim_out.vcd`.
