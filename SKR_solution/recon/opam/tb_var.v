`timescale 1ns/1ps
module tb_var;
  reg clk=0, rst_n=0, enable=0, I=0;
  wire [7:0] O; wire s;
  puzzle u(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(s));
  reg [121:0] KEY;
  integer cyc, mode, ti; reg [255:0] txt;
  always #5 clk=~clk;
  reg [121:0] KEYM [0:0];
  initial $readmemb("recon/opam/key.mem", KEYM);
  initial begin
    if (!$value$plusargs("mode=%d", mode)) mode=0;
    #1 KEY = KEYM[0]; txt=0; ti=0;
    for (cyc=0; cyc<220; cyc=cyc+1) begin
      rst_n=(cyc>=3); enable=(cyc>=4);
      I = (cyc>=4 && cyc<126) ? KEY[121-(cyc-4)] : 1'b0;
      if (mode==1 && cyc>=126 && cyc<130) I = 1'b1;          // extra ones after the key
      if (mode==2 && cyc>=126) I = (cyc%2);                    // keep toggling after key
      if (mode==3 && cyc>=4 && cyc<126) I = 1'b1;              // all ones
      if (mode==4 && cyc==4) I = 1'b1;                          // one bit flipped
      if (mode==5) enable = (cyc>=4 && cyc<126);                // enable dropped after key
      @(posedge clk); #1;
      if (O!=0 && (ti==0 || txt[7:0]!=O)) begin txt={txt[247:0],O}; ti=ti+1; end
      if (cyc==124 || cyc==127 || cyc==140) $display("mode=%0d cyc=%0d s197=%b s248=%b g205=%b g180=%b g243=%b cnt=%0d", mode, cyc, u.\g__197.IQ , u.\g__248.IQ , u.\g__205.IQ , u.\g__180.IQ , u.\g__243.IQ ,
         {u.\g__201.IQ ,u.\g__215.IQ ,u.\g__224.IQ ,u.\g__393.IQ ,u.\g__236.IQ ,u.\g__233.IQ ,u.\g__190.IQ ,u.\g__183.IQ });
    end
    $display("mode=%0d text=\"%0s\"", mode, txt);
    $finish;
  end
endmodule
