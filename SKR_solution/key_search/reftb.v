`timescale 1ns/1ps
module reftb;
  reg clk=0, rst_n=0, enable=1, I=0;
  wire [7:0] O; wire success;
  integer k;
  reg [124:0] KEY = 125'b00000000000101000100100000100000010000000100001010000010000001000001000000101000000000000101010100000000000010000101010000000;
  puzzle dut(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(success));
  always #5 clk = ~clk;
  initial begin
    $dumpfile("ref_key.vcd"); $dumpvars(0, reftb);
    rst_n=0; I=0;
    @(posedge clk); #1 rst_n=1;
    for (k=1; k<125; k=k+1) begin
      I = KEY[k];
      @(posedge clk); #1;
      if (success===1'b1) $display("SUCCESS=1 at cycle %0d", k);
    end
    repeat(20) @(posedge clk);
    $display("final success=%b", success);
    $finish;
  end
endmodule