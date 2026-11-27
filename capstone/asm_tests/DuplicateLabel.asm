// DuplicateLabel.asm - Test program for K mod 3 = 2 extra feature
// Student: Harsh Saini | Roll no.: 2501350092 | K = 92 | K mod 3 = 2
// Demonstrates that defining the same label (LOOP) twice prints a warning
// instead of silently overwriting or crashing.

(LOOP)
    @R0
    D=M
    @1
    D=D+A
(LOOP)              // Duplicate label: should trigger a warning
    @R1
    M=D
    @LOOP
    0;JMP
