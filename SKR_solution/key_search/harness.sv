module harness(input clk, input I);
  reg rst_n = 0;
  wire [7:0] O; wire success;
  reg started = 0;
  always @(posedge clk) begin rst_n <= 1; started <= 1; end
  puzzle dut(.clk(clk), .rst_n(rst_n), .enable(1'b1), .I(I), .O(O), .success(success));
  always @(posedge clk) if (started) cover(success);
endmodule
