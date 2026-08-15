`timescale 1ns/1ps
module tb_touch;
  reg clk=0, rst_n=0, enable=0, I=0; wire [7:0] O; wire s;
  puzzle u(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(s));
  reg [121:0] M [0:0]; reg [121:0] K; integer cyc, ti; reg [255:0] txt=0;
  always #5 clk=~clk;
  initial begin
    $readmemb("recon/opam/touch.mem", M); K=M[0]; ti=0;
    for (cyc=0;cyc<200;cyc=cyc+1) begin
      rst_n=(cyc>=3); enable=(cyc>=4); I=(cyc>=4&&cyc<126)?K[121-(cyc-4)]:1'b0;
      @(posedge clk); #1;
      if (O!=0 && (ti==0 || txt[7:0]!=O)) begin txt={txt[247:0],O}; ti=ti+1; end
      if (cyc==127) $display("g197=%b g248=%b g205=%b g254=%b", u.\g__197.IQ , u.\g__248.IQ , u.\g__205.IQ , u.\g__254.IQ );
    end
    $display("text=\"%0s\"", txt); $finish;
  end
endmodule
