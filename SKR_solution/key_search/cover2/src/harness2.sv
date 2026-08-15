module harness(input clk, input I);
  reg [7:0] cnt = 0;
  always @(posedge clk) if (cnt < 8'hff) cnt <= cnt + 1;
  wire rst_n  = (cnt >= 3);   // low for cnt 0,1,2
  wire enable = (cnt >= 4);   // high from cnt 4 on
  wire [7:0] O; wire success;
  puzzle dut(.clk(clk), .rst_n(rst_n), .enable(enable), .I(I), .O(O), .success(success));
  always @(posedge clk) if (cnt >= 4) cover(success);
endmodule
