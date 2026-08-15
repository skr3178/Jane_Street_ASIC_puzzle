`timescale 1ns/1ps
module tb;
  reg clk=0, rst_n=0, enable=0, I=0;
  wire [7:0] O; wire success; wire [91:0] STATE;
  reg [0:0] km [0:121];
  integer cyc, b;
  puzzle dut(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(success),.STATE(STATE));
  always #5 clk=~clk;
  initial begin
    $readmemb("input.mem", km);
    b=0;
    for (cyc=0; cyc<130; cyc=cyc+1) begin
      rst_n = (cyc>=3);
      enable = (cyc>=4);
      if (cyc>=4 && b<122) begin I=km[b]; b=b+1; end else I=1'b0;
      @(posedge clk); #1;
    end
    $display("STATE=%b", STATE);
    $finish;
  end
endmodule
