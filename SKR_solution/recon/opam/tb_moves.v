`timescale 1ns/1ps
module tb_moves;
  reg clk=0, rst_n=0, enable=0, I=0; wire [7:0] O; wire s;
  puzzle u(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(s));
  reg [121:0] M [0:399]; reg [121:0] K; integer n, cyc;
  always #5 clk=~clk;
  initial begin
    $readmemb("recon/opam/moves.mem", M);
    for (n=0;n<400;n=n+1) begin
      K=M[n];
      for (cyc=0;cyc<125;cyc=cyc+1) begin
        rst_n=(cyc>=3); enable=(cyc>=4);
        I=(cyc>=4&&cyc<126)?K[121-(cyc-4)]:1'b0;
        @(posedge clk); #1;
      end
      // at cyc=124 (g__180=1,g__243=0): report the non-pair literals
      $display("sol %0d: g205=%b g254=%b g258=%b g259=%b | g186=%b g231=%b g240=%b g255=%b | pairs_ok=%b", n,
        u.\g__205.IQ , u.\g__254.IQ , u.\g__258.IQ , u.\g__259.IQ , u.\g__186.IQ , u.\g__231.IQ , u.\g__240.IQ , u.\g__255.IQ ,
        (~u.\g__261.IQ & u.\g__198.IQ & u.\g__262.IQ & ~u.\g__219.IQ & ~u.\g__204.IQ & u.\g__260.IQ & ~u.\g__188.IQ & u.\g__228.IQ & u.\g__207.IQ & ~u.\g__184.IQ & ~u.\g__238.IQ & u.\g__202.IQ & ~u.\g__200.IQ & u.\g__242.IQ & u.\g__226.IQ & ~u.\g__253.IQ & ~u.\g__218.IQ & u.\g__217.IQ & u.\g__214.IQ & ~u.\g__179.IQ & ~u.\g__263.IQ & u.\g__216.IQ & ~u.\g__244.IQ & u.\g__222.IQ & u.\g__249.IQ & ~u.\g__211.IQ & ~u.\g__234.IQ & u.\g__203.IQ & ~u.\g__189.IQ & u.\g__210.IQ & u.\g__213.IQ & ~u.\g__230.IQ & ~u.\g__257.IQ & u.\g__194.IQ & ~u.\g__252.IQ & u.\g__192.IQ & u.\g__195.IQ & ~u.\g__182.IQ & ~u.\g__232.IQ & u.\g__241.IQ & u.\g__229.IQ & ~u.\g__193.IQ & ~u.\g__235.IQ & u.\g__225.IQ ));
    end
    $finish;
  end
endmodule
