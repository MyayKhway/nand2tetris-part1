(BLACKLOOP)
	@KBD
	D=M
	@WHITELOOP
	D;JEQ		//jump to white loop if equals 0
	@24575
	D=M
	@WHITELOOP	
	D;JLT		//termination condition; if the last word of the screen is filled, go to another loop black or white whatever

	@index
	D=M		//this index is set to zero
	@SCREEN
	D=A+D
	A=D		//the addres we want to change = the start of the screen + index value
	M=-1
	@index
	M=M+1		//increment the index
	@BLACKLOOP
	0;JMP		//restart the loop
/////////////////////
(WHITELOOP)
	@KBD
	D=M
	@BLACKLOOP
	D;JGT		//if a key is pressed while the screen is being cleared, blacken the screen
	
	@index
	D=M
	@SCREEN
	D=A+D
	A=D
	M=0		//clear the screen
	@index
	M=M-1
	@WHITELOOP
	0;JMP

