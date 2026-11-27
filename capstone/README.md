# Capstone Project – Make the Computer Draw a Box

- **Student Name:** Harsh Saini
- **Roll Number:** `2501350092`
- **University & Program:** K.R. Mangalam University (School of Engineering & Technology) — B.Tech CSE (FSD), Semester III, Section B
- **Course:** Nand to Tetris – I (`ETCCNT301`)
- **Instructor:** Neetu Chauhan

## Personal Number `K` Derivations

`K` = last two digits of roll number `2501350092` = **`92`**

- **`K mod 3 = 92 mod 3 = 2`** → **Extra assembler feature:** Print a warning if the same label is written twice.
- **`K mod 4 = 92 mod 4 = 0`** → **Box width:** `16 × ((92 mod 4) + 1) = 16 × 1 = 16` pixels (`1` word per row from the left edge).
- **Box vertical span:** Starts at row **`92`**, `20` rows tall (**rows `92` to `111`** inclusive).
- **First screen RAM address:** `SCREEN + 32 × 92 = 16384 + 2944 = 19328`.

## Files

```text
CPU.hdl, Memory.hdl, Computer.hdl   -> Part A (the Hack computer)
other .hdl files                    -> Lab chips (gates, ALU, PC, Register, Bit) used by CPU/Memory
*.tst, *.cmp, *.hack                -> Official test scripts and compare files for Part A
assembler.py                        -> Part B (Two-pass Hack assembler in Python with K mod 3 = 2 warning)
asm_tests/                          -> Add, Max, Rect, Pong, and DuplicateLabel test programs
asm_tests/official/                 -> Official Nand2Tetris assembler outputs for Add, Max, Rect, Pong
check_assembler.py / .sh            -> Automated verifier comparing against official outputs + K=92 checks
Box.asm                             -> Part C (keyboard-triggered 16x20 box at row 92..111)
Box.hack                            -> Binary assembled from Box.asm using my assembler.py
steps/                              -> Incremental build steps (Step1_Dash -> Step2_WideDash -> Step3_Box)
```

## How to Run

### Part A — Hardware Verification

Open the Nand2Tetris **Hardware Simulator** (desktop tool or Web IDE), load and run:
- `CPU.tst`
- `Memory.tst`
- `ComputerAdd.tst`
- `ComputerMax.tst`
- `ComputerRect.tst`

`Memory.hdl` uses the simulator's built-in `RAM16K`, `Screen`, and `Keyboard` chips (using a pure register-based `RAM16K` is too slow for simulation), while `CPU.hdl`, `Computer.hdl`, and the arithmetic/logic/PC/register chips come from the lab implementations.

### Part B — Two-Pass Assembler (`K mod 3 = 2`)

Assemble any `.asm` program:

```bash
python assembler.py asm_tests/Pong.asm
```

Run the full automated verification suite (`Add`, `Max`, `Rect`, `Pong`, `Box`, and duplicate-label warning check):

```bash
python check_assembler.py
```

To demonstrate the **`K mod 3 = 2`** extra feature (printing a warning when the same label is written twice):

```bash
python assembler.py asm_tests/DuplicateLabel.asm
```

Sample output when a duplicate label appears:

```text
Warning (line 11): label '(LOOP)' was already defined on line 6 (ROM[0]); keeping original ROM address.
OK: 8 instructions written to asm_tests/DuplicateLabel.hack
```

### Part C — Interactive Box (`Box.asm` → `Box.hack`)

Assemble `Box.asm` using your own assembler:

```bash
python assembler.py Box.asm
```

Then open the **CPU Emulator**, load `Box.hack`, set **View → Screen**, run the program, and hold any key:
- A **`16 × 20` pixel black box** appears on the left edge at **rows `92` to `111`** (`RAM[19328]` to `RAM[19936]`, stepping by `32` words per row).
- Releasing the key clears the box back to white (`0`).
