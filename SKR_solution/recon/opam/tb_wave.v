`timescale 1ns/1ps
// Per-cycle CSV of the reference-cell sim for two runs: the key, and the key with one star moved (TRY AGAIN)
module tb_wave;
  reg clk=0, rst_n=0, enable=0, I=0; wire [7:0] O; wire success;
  puzzle dut(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(success));
  reg [121:0] M [0:0]; reg [121:0] K; integer cyc, mode, f;
  always #5 clk=~clk;
  initial begin
    $readmemb("recon/opam/key.mem", M);
    for (mode=0; mode<2; mode=mode+1) begin
      K=M[0]; if (mode==1) begin K[121-7]=0; K[121-8]=1; end   // move the star at cell 7 to cell 8 (still row 0)
      f=$fopen(mode==0 ? "recon/opam/wave_key.csv" : "recon/opam/wave_wrong.csv","w");
      $fwrite(f,"cyc,rst_n,enable,I,success,O\n");
      for (cyc=0; cyc<160; cyc=cyc+1) begin
        rst_n=(cyc>=3); enable=(cyc>=4);
        I=(cyc>=4&&cyc<126)?K[121-(cyc-4)]:1'b0;
        @(posedge clk); #1;
        $fwrite(f,"%0d,%b,%b,%b,%b,%0d\n",cyc,rst_n,enable,I,success===1'b1,(O===8'bxxxxxxxx)?0:O);
      end
      $fclose(f);
    end
    $finish;
  end
endmodule
