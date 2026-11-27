// Step 2 - dash using loop: paint (92 mod 4) + 1 = 1 word (16 pixels) of row 92.
// Student: Harsh Saini | Roll no.: 2501350092 | K = 92
    @SCREEN
    D=A
    @2944
    D=D+A
    @ptr
    M=D             // ptr = 19328 (first word of row 92)
    @1
    D=A
    @cols
    M=D             // cols = 1 word to paint
(WORD)
    @ptr
    A=M
    M=-1            // RAM[ptr] = -1 (black)
    @ptr
    M=M+1           // ptr = ptr + 1
    @cols
    MD=M-1          // cols = cols - 1
    @WORD
    D;JGT           // repeat while cols > 0
(END)
    @END
    0;JMP
