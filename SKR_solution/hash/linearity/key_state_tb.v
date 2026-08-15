`timescale 1ns/1ps
module ktb;
  reg clk=0,rst_n=0,enable=0,I=0; integer cyc; wire [7:0] O; wire success; wire [91:0] STATE;
  reg [126:0] KEY=127'b0000000000101000100100000100000010000000100001010000010000001000001000000101000000000000101010100000000000010000101010000000000;
  reg done=0;
  puzzle dut(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(success),.STATE(STATE));
  always #5 clk=~clk;
  initial begin
    for(cyc=0;cyc<200;cyc=cyc+1) begin
      rst_n=(cyc>=3); enable=(cyc>=4);
      if(cyc-1>=0 && cyc-1<127) I=KEY[cyc-1]; else I=0;
      @(posedge clk); #1;
      if(success===1'b1 && !done) begin
        done=1; $display("ACCEPT cyc=%0d STATE=%b", cyc, STATE);
      end
    end
    $finish;
  end
endmodule
