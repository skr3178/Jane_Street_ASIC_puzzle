`timescale 1ns/1ps
module tb_ref;
  reg clk=0, rst_n=0, enable=0, I=0; wire [7:0] O; wire success;
  puzzle dut(.clk(clk),.rst_n(rst_n),.enable(enable),.I(I),.O(O),.success(success));
  reg [121:0] M [0:0]; reg [121:0] K; integer cyc, ti, off, nsucc; reg [255:0] txt;
  always #5 clk=~clk;
  initial begin
    $readmemb("recon/opam/key.mem", M); K=M[0];
    for (off=-1; off<=1; off=off+1) begin        // try the key at 3 alignments
      txt=0; ti=0; nsucc=0;
      for (cyc=0; cyc<200; cyc=cyc+1) begin
        rst_n=(cyc>=3); enable=(cyc>=4);
        I=(cyc-4-off>=0 && cyc-4-off<122) ? K[121-(cyc-4-off)] : 1'b0;
        @(posedge clk); #1;
        if (success===1'b1) nsucc=nsucc+1;
        if (O!==8'h00 && O!==8'hxx && (ti==0 || txt[7:0]!=O)) begin txt={txt[247:0],O}; ti=ti+1; end
      end
      $display("offset=%0d  success_cycles=%0d  text=\"%0s\"", off, nsucc, txt);
      // re-reset between attempts (rst_n toggled by the loop start)
    end
    $finish;
  end
endmodule
