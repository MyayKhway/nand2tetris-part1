// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

//set n to R1
@R1
D=M
@n
M=D

//set i to 1
@i
M=1

//set product to 0
@product
M=0

//LOOP
(LOOP)
	//if i > n jump to stop
	@i
	D=M
	@n
	D=D-M
	@STOP
	D;JGT

	//add the R0 , R1 times
	@product
	D=M
	@R0
	D=D+M
	@product
	M=D
	@i
	M=M+1
	@LOOP
	0;JMP

//stop
(STOP)
	@product
	D=M
	@R2
	M=D

//end loop
(END)
	@END
	0;JMP	

