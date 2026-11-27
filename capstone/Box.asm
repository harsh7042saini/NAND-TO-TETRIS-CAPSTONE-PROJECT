// Box.asm - Capstone Part C
// Student: Harsh Saini      Roll no.: 2501350092      K = 92
// Course : Nand to Tetris - I (ETCCNT301) | Instructor: Neetu Chauhan
//
// While any key is pressed, a black box appears on the screen;
// when the key is released, the box disappears.
//
// Box specification for K = 92:
//   starts at row K = 92, is 20 rows tall        -> rows 92 .. 111
//   width = 16 * ((K mod 4) + 1) = 16 * 1 = 16px -> 1 word per row from the left edge
//
// Screen memory layout: row r starts at SCREEN + 32*r (32 words/row, 16 pixels/word).
//   First row of the box: SCREEN + 32*92 = 16384 + 2944 = 19328
//   Writing -1 (16 bits = 1) turns all 16 pixels black; writing 0 turns them white.
//
// Variables (RAM[16] onwards, assigned by assembler.py):
//   color - pixel value to write: 0 = white, -1 = black
//   addr  - start address of the current row in Screen RAM
//   rows  - remaining rows to paint (counts down from 20 to 0)
//   ptr   - current word address inside the active row
//   cols  - remaining words to paint in the row (counts down from 1 to 0)

(LOOP)
    // ---- 1. Read keyboard and select box color ----
    @KBD
    D=M                 // D = key code (0 when no key is pressed)
    @color
    M=0                 // default to white
    @SETUP
    D;JEQ               // if no key pressed -> draw white
    @color
    M=-1                // key pressed -> draw black

(SETUP)
    // ---- 2. Point addr to the first word of row 92 ----
    @SCREEN
    D=A
    @2944               // 32 * 92 (row offset for K = 92)
    D=D+A
    @addr
    M=D                 // addr = 16384 + 2944 = 19328
    @20                 // box height = 20 rows (rows 92..111)
    D=A
    @rows
    M=D                 // rows = 20

(ROW)
    // ---- 3. Paint one row: 1 word starting at addr ----
    @addr
    D=M
    @ptr
    M=D                 // ptr = addr
    @1                  // box width in words: (92 mod 4) + 1 = 1
    D=A
    @cols
    M=D                 // cols = 1

(WORD)
    @color
    D=M                 // D = color (0 or -1)
    @ptr
    A=M                 // A = current screen word address
    M=D                 // RAM[ptr] = color (16 pixels)
    @ptr
    M=M+1               // ptr = ptr + 1 (next 16-pixel word to the right)
    @cols
    MD=M-1              // cols = cols - 1
    @WORD
    D;JGT               // if words remain in this row -> continue

    // ---- 4. Advance one row down (+32 words) ----
    @32
    D=A
    @addr
    M=D+M               // addr = addr + 32
    @rows
    MD=M-1              // rows = rows - 1
    @ROW
    D;JGT               // if rows remain -> paint next row

    @LOOP
    0;JMP               // repeat continuously
