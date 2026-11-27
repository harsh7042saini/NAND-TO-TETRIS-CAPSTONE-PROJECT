// Step 1 - one dash: paint ONE word (16 pixels) black at the start of row 92.
// Student: Harsh Saini | Roll no.: 2501350092 | K = 92
// Address = SCREEN + 32*92 = 16384 + 2944 = 19328
    @SCREEN
    D=A
    @2944
    D=D+A           // D = 19328
    @addr
    M=D             // addr = 19328
    A=D             // A = 19328
    M=-1            // RAM[19328] = -1 -> 16 black pixels
(END)
    @END
    0;JMP           // stop here forever
