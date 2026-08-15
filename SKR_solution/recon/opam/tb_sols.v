`timescale 1ns/1ps
module tb_sols;
  reg clk=0, rst_n=0, enable=0, I=0; wire [7:0] O; wire s;
  puzzle u(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(s));
  reg [121:0] M [0:495]; reg [121:0] K; integer n, cyc, nsucc=0;
  always #5 clk=~clk;
  initial begin
    $readmemb("recon/opam/sols.mem", M);
    for (n=0;n<496;n=n+1) begin
      K=M[n];
      for (cyc=0;cyc<130;cyc=cyc+1) begin
        rst_n=(cyc>=3); enable=(cyc>=4);
        I=(cyc>=4&&cyc<126)?K[121-(cyc-4)]:1'b0;
        @(posedge clk); #1;
      end
      if (s) begin nsucc=nsucc+1; $display("solution %0d UNLOCKS  (%0s)", n, "OK"); end
    end
    $display("unlocking solutions: %0d / 496", nsucc);
    $finish;
  end
endmodule
