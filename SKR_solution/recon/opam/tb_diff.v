`timescale 1ns/1ps
// Differential testbench: puzzle (ground truth from netlist) vs puzzle_reconstructed
module tb_diff;
  reg clk=0, rst_n=0, enable=0, I=0;
  wire [7:0] O_ref, O_rec; wire s_ref, s_rec;
  puzzle               u_ref(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O_ref),.success(s_ref));
  puzzle_reconstructed u_rec(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O_rec),.success(s_rec));
  reg [121:0] KEY = 122'b00000001010100001000000000000101010100000000000010100000010000010000001000001010000100000001000000100000100100010100000000;
  integer cyc, run, mism=0, seed=7, k, nsucc=0;
  reg [255:0] txt; integer ti;
  task do_run(input integer mode, input integer ncyc, input integer show);
    begin
      txt = 0; ti = 0;
      for (cyc=0; cyc<ncyc; cyc=cyc+1) begin
        rst_n  = (cyc >= 3);
        enable = (cyc >= 4);
        if (mode==0)      I = (cyc>=4 && cyc<126) ? KEY[121-(cyc-4)] : 1'b0;   // key, MSB-first as listed
        else if (mode==1) I = (cyc>=4 && cyc<126) ? KEY[cyc-4] : 1'b0;         // key, LSB-first
        else if (mode==2) I = 1'b0;
        else              I = $random(seed);
        @(posedge clk); #1;
        if (O_ref!==O_rec || s_ref!==s_rec) begin
          mism = mism+1;
          if (mism<10) $display("MISMATCH mode=%0d cyc=%0d ref O=%h s=%b rec O=%h s=%b", mode, cyc, O_ref, s_ref, O_rec, s_rec);
        end
        if (s_ref) nsucc = nsucc+1;
        if (show && O_ref!=0 && (ti==0 || txt[7:0]!=O_ref)) begin txt = {txt[247:0], O_ref}; ti=ti+1; end
      end
      if (show) $display("mode=%0d success_cycles=%0d text=\"%0s\"", mode, nsucc, txt);
      nsucc = 0;
    end
  endtask
  always #5 clk = ~clk;
  initial begin
    do_run(0, 400, 1);
    do_run(1, 400, 1);
    do_run(2, 400, 1);
    for (run=0; run<40; run=run+1) do_run(3, 300, 0);
    $display("TOTAL MISMATCHES = %0d", mism);
    $finish;
  end
endmodule
