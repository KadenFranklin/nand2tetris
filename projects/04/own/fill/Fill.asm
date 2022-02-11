// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

// Put your code here.
(BEGIN)
	@24576
	D=A
	@keyboard
	M=D
 (CHECK_KEYBOARD)
	@24575
	D=A
	@current
	M=D
	
	@keyboard
	A=M
	D=M
	@fillvalue
	M=-1
	@DRAW
	D;JNE
	
	@fillvalue
	M=0
(DRAW)
	@fillvalue
	D=M
	@current
	A=M
	M=D

	@current
	D=M
	@16384
	D=D-A
	@CHECK_KEYBOARD
	D;JLE

	@current
	M=M-1

	@DRAW
	0;JMP