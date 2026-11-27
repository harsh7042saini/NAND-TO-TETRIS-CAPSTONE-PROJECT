// Step 3 - the box: 20 rows of 1 word at row 92..111, without keyboard check yet.
// Student: Harsh Saini | Roll no.: 2501350092 | K = 92
    @SCREEN
    D=A
    @2944
    D=D+A
    @addr
    M=D             // addr = first word of row 92 (19328)
    @20
    D=A
    @rows
    M=D             // rows = 20
(ROW)
    @addr
    D=M
    @ptr
    M=D             // ptr = addr
    @1
    D=A
    @cols
    M=D             // cols = (92 mod 4) + 1 = 1
(WORD)
    @ptr
    A=M
    M=-1            // paint one word black
    @ptr
    M=M+1
    @cols
    MD=M-1
    @WORD
    D;JGT           // next word in this row
    @32
    D=A
    @addr
    M=D+M           // addr = addr + 32 (one row down)
    @rows
    MD=M-1
    @ROW
    D;JGT           // next row
(END)
    @END
    0;JMP
