`timescale 1ns/1ps
module tb_trace;
  reg clk=0, rst_n=0, enable=0, I=0;
  wire [7:0] O; wire s;
  puzzle_reconstructed u(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(s));
  reg [121:0] KEY = 122'b00000001010100001000000000000101010100000000000010100000010000010000001000001010000100000001000000100000100100010100000000;
  integer cyc, mode;
  always #5 clk=~clk;
  initial begin
    if (!$value$plusargs("mode=%d", mode)) mode=0;
    for (cyc=0; cyc<200; cyc=cyc+1) begin
      rst_n=(cyc>=3); enable=(cyc>=4);
      if (mode==0) I = (cyc>=4 && cyc<126) ? KEY[121-(cyc-4)] : 0;
      else if (mode==1) I = 0;
      else I = (cyc>=4 && cyc<126) ? (cyc==4) : 0;   // single 1 at first position
      @(posedge clk); #1;
      if (cyc>=118 && cyc<=175)
        $display("cyc=%0d I=%b s197=%b s248=%b g243=%b g180=%b cnt8={%b%b%b%b%b%b%b%b} idx={%b%b%b%b} data={%b%b%b%b%b%b%b%b} g205=%b O=%h '%c'",
          cyc, I, u.g__197, u.g__248, u.g__243, u.g__180,
          u.g__201,u.g__393,u.g__236,u.g__233,u.g__224,u.g__215,u.g__190,u.g__183,
          u.g__539,u.g__11,u.g__10,u.g__9,
          u.g__405,u.g__206,u.g__13,u.g__208,u.g__227,u.g__14,u.g__256,u.g__12, u.g__205, O, (O>=32&&O<127)?O:".");
    end
    $finish;
  end
endmodule
