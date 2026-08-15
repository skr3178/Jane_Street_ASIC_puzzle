# Warm-up (sample) — recovering the circuit's true purpose

The warm-up design `adder_demo` (in `warmup/`) is the sample Jane Street shipped so
you can calibrate your tools on a design whose answer is known. We established its
true purpose **two independent ways**.

## Result

```
success (S) = 1   if and only if   A + B == 496
```
where `A` and `B` are two 8-bit values shifted in serially (one bit per clock, MSB
first) through two 8-bit shift registers.

## Route 1 — read it from the given source (ground truth)

The warm-up *comes with* its RTL, `warmup/00_source.v`. It spells the function out:

```verilog
module comparator496 (input [8:0] val, output eq);
    assign eq = (val == 9'd496);          // <- the check
endmodule

module adder_demo(...);
    shift_register sr_a(... .serial_in(A), .parallel_out(a_reg));  // 8-bit
    shift_register sr_b(... .serial_in(B), .parallel_out(b_reg));  // 8-bit
    adder8         add0(.a(a_reg), .b(b_reg), .sum(sum));          // A+B
    comparator496  cmp0(.val(sum), .eq(S));                        // ==496 -> S
endmodule
```

So for the sample the purpose is handed to you: two shift registers → adder →
"==496" comparator → `S`.

## Route 2 — re-derive it blind from the netlist (proving the method)

To show the method works *without* peeking at the source, we recovered the same
fact from the gate netlist `warmup/01_netlist.v` alone, using a SAT solver.

Script: [eqc/blind_purpose_sat.ys](eqc/blind_purpose_sat.ys). The idea:

1. Load the netlist with real cell functions (`read_liberty -wb`), drop the
   physical fill cells, `flatten`.
2. **Delete the flip-flops** (`delete */t:$_DFF_PN0_`). This cuts the sequential
   loop and turns the 16 register outputs (`a_reg[7:0]`, `b_reg[7:0]`) into free
   inputs — i.e. "for any register contents, when is `S` true?"
3. Ask SAT to enumerate every assignment of those 16 bits that makes `S=1`:
   ```
   sat -show a_reg[7..0],b_reg[7..0] -set S 1 -all -max 32
   ```

Run it:
```bash
nix-shell ~/Downloads/tiny-gpu/librelane --run \
  "yosys -s SKR_solution/eqc/blind_purpose_sat.ys"
```

**Result: 15 solutions, and every one sums to 496:**

```
 a=241 b=255   a=242 b=254   a=243 b=253   a=244 b=252   a=245 b=251
 a=246 b=250   a=247 b=249   a=248 b=248   a=249 b=247   a=250 b=246
 a=251 b=245   a=252 b=244   a=253 b=243   a=254 b=242   a=255 b=241
```

(Exactly the 15 pairs of 8-bit numbers that add to 496 — 241 is the smallest, since
`a,b ≤ 255` forces `a ≥ 496-255`.) The solver recovered "A+B==496" from gates alone,
with no reference to the source. The two routes agree.

## Why this mattered for the puzzle

This is the calibration step: it proved the "delete the flops, ask SAT what makes the
output fire" technique genuinely recovers a lock's accepting condition. We then scaled
the same idea to the real puzzle — except there the search used bounded model checking
(`cover(success)`) over 92 flops, and the accepting condition does **not** collapse
into a clean human statement like "==496" (it's a scrambled 57-bit check), which is
why on the puzzle we can open the lock without fully naming its function. See
`SOLUTION.md` and `debug_plan.md`.
