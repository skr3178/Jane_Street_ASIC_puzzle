`timescale 1ns/1ps
module reftb;
  reg clk=0, rst_n=0, enable=0, I=0; integer k, cyc;
  wire [7:0] O; wire success;
  reg succ_latch=0;
  reg [126:0] KEY = 127'b0000000000101000100100000100000010000000100001010000010000001000001000000101000000000000101010100000000000010000101010000000000;
  puzzle dut(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(success));
  always #5 clk=~clk;
  always @(posedge clk) if (success===1'b1) succ_latch<=1;
  initial begin
    $dumpfile("full.vcd"); $dumpvars(0, reftb);
    for (cyc=0; cyc<400; cyc=cyc+1) begin
      rst_n=(cyc>=3); enable=(cyc>=4);
      if (cyc-1>=0 && cyc-1<127) I=KEY[cyc-1]; else I=0;   // offset=1
      @(posedge clk); #1;
    end
    $display("SUCCESS EVER HIGH: %b", succ_latch);
    $finish;
  end
endmodule
