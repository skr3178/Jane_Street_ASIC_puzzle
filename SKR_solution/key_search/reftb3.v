`timescale 1ns/1ps
module reftb;
  reg clk=0, I=0; integer k;
  reg [126:0] KEY = 127'b0000000000101000100100000100000010000000100001010000010000001000001000000101000000000000101010100000000000010000101010000000000;
  wire dO; // unused
  harness UUT(.clk(clk), .I(I));
  always #5 clk=~clk;
  initial begin
    $dumpfile("ref3.vcd"); $dumpvars(0, reftb);
    for (k=0; k<127; k=k+1) begin
      I = KEY[k];
      @(posedge clk); #1;
      if (UUT.success===1'b1) $display("REF-SUCCESS at cycle %0d (cnt=%0d)", k, UUT.cnt);
    end
    repeat(30) @(posedge clk);
    $display("final success=%b", UUT.success);
    $finish;
  end
endmodule
