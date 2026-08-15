`timescale 1ns/1ps
module reftb;
  reg clk=0, rst_n=0, enable=0, I=0; integer k, cyc; integer OFF;
  wire [7:0] O; wire success;
  reg [126:0] KEY = 127'b0000000000101000100100000100000010000000100001010000010000001000001000000101000000000000101010100000000000010000101010000000000;
  puzzle dut(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(success));
  always #5 clk=~clk;
  initial begin
    OFF = $value$plusargs("off=%d", OFF) ? OFF : 0;
    $dumpfile("swp.vcd"); $dumpvars(0, reftb);
    cyc=0;
    for (k=0; k<127+10; k=k+1) begin
      rst_n  = (cyc >= 3);
      enable = (cyc >= 4);
      if (cyc-OFF >= 0 && cyc-OFF < 127) I = KEY[cyc-OFF]; else I = 0;
      @(posedge clk); #1;
      if (success===1'b1) begin $display("OFF=%0d SUCCESS at cyc=%0d", OFF, cyc); end
      cyc=cyc+1;
    end
    $display("OFF=%0d final success=%b", OFF, success);
    $finish;
  end
endmodule
