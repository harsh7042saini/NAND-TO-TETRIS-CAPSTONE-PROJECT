#!/usr/bin/env python3
"""
assembler.py - Two-pass Hack Assembler (Nand to Tetris, Project 6 / Capstone)

Student Name : Harsh Saini
Roll Number  : 2501350092   -> K = 92
University   : K.R. Mangalam University (B.Tech CSE FSD, Sem III, Sec B)
Course       : Nand to Tetris - I (ETCCNT301) | Instructor: Neetu Chauhan
K mod 3 = 2  : Extra feature - print a warning if the same label is written twice.

Usage:
    python assembler.py Prog.asm            # writes Prog.hack next to Prog.asm
    python assembler.py Prog.asm Out.hack   # writes to Out.hack instead

Two-pass translation:
    Pass 1 - strip comments and whitespace, map every (LABEL) to its ROM address,
             and emit a warning if any label name is declared more than once.
    Pass 2 - translate A-instructions and C-instructions into 16-bit binary words;
             allocate unseen variables sequentially starting at RAM[16].
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# 1. Hack machine-language lookup tables
# ---------------------------------------------------------------------------

# comp -> 7 bits: a c1 c2 c3 c4 c5 c6
COMP = {
    "0":   "0101010", "1":   "0111111", "-1":  "0111010",
    "D":   "0001100", "A":   "0110000", "M":   "1110000",
    "!D":  "0001101", "!A":  "0110001", "!M":  "1110001",
    "-D":  "0001111", "-A":  "0110011", "-M":  "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101",
}

# dest -> 3 bits: d1 d2 d3 (A, D, M)
DEST = {
    "":    "000", "M":   "001", "D":   "010", "MD":  "011",
    "A":   "100", "AM":  "101", "AD":  "110", "AMD": "111",
}

# jump -> 3 bits: j1 j2 j3 (<0, =0, >0)
JUMP = {
    "":    "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}

# Predefined symbols required by the Hack specification
PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
}
for _i in range(16):
    PREDEFINED[f"R{_i}"] = _i

# Valid Hack symbol characters; cannot begin with a digit
SYMBOL_RE = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")

FIRST_VARIABLE_ADDRESS = 16


# ---------------------------------------------------------------------------
# 2. Errors and assembly result container
# ---------------------------------------------------------------------------
class AsmError(Exception):
    """Raised when an invalid assembly instruction is encountered."""

    def __init__(self, line_no, message):
        super().__init__(f"Line {line_no}: invalid instruction - {message}")
        self.line_no = line_no


class AssembleResult(int):
    """Behaves as the assembled instruction count while carrying warnings and metadata."""

    def __new__(cls, count, warnings=None):
        obj = super().__new__(cls, count)
        obj.count = count
        obj.warnings = warnings or []
        return obj


# ---------------------------------------------------------------------------
# 3. Parsing and translation passes
# ---------------------------------------------------------------------------
def clean(line):
    """Strip inline // comments and all whitespace from a source line."""
    line = line.split("//", 1)[0]
    return "".join(line.split())


def read_instructions(path):
    """Read source lines and keep non-empty cleaned instructions with line numbers."""
    instructions = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, start=1):
            text = clean(raw)
            if text:
                instructions.append((line_no, text))
    return instructions


def first_pass(instructions):
    """
    Build the symbol table with ROM addresses for all (LABEL) declarations.

    K mod 3 = 2 feature: if the same label name appears more than once, record
    a warning identifying both occurrences and retain the first definition.
    """
    symbols = dict(PREDEFINED)
    label_lines = {}
    warnings = []
    rom_address = 0

    for line_no, text in instructions:
        if text.startswith("("):
            if not text.endswith(")"):
                raise AsmError(line_no, f"label {text!r} is missing ')'")
            name = text[1:-1]
            if not SYMBOL_RE.match(name):
                raise AsmError(line_no, f"{name!r} is not a valid label name")
            if name in label_lines:
                first_line = label_lines[name]
                first_addr = symbols[name]
                warnings.append(
                    f"Warning (line {line_no}): label '({name})' was already defined on "
                    f"line {first_line} (ROM[{first_addr}]); keeping original ROM address."
                )
                continue
            if name in symbols:
                raise AsmError(line_no, f"label {name!r} conflicts with a predefined symbol")
            symbols[name] = rom_address
            label_lines[name] = line_no
        else:
            rom_address += 1

    return symbols, warnings


def translate_a(text, line_no, symbols, next_var):
    """Translate an @value instruction into '0' + 15-bit binary string."""
    value = text[1:]
    if value == "":
        raise AsmError(line_no, "'@' must be followed by a number or a symbol")
    if value.isdigit():
        number = int(value)
        if number > 32767:
            raise AsmError(line_no, f"@{number} is too large (max 32767)")
    elif SYMBOL_RE.match(value):
        if value not in symbols:
            symbols[value] = next_var
            next_var += 1
        number = symbols[value]
    else:
        raise AsmError(line_no, f"{value!r} is not a valid number or symbol")
    return "0" + format(number, "015b"), next_var


def translate_c(text, line_no):
    """Translate dest=comp;jump into '111' + comp(7) + dest(3) + jump(3)."""
    dest, comp, jump = "", text, ""
    if "=" in comp:
        dest, comp = comp.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    if comp not in COMP:
        raise AsmError(line_no, f"unknown computation {comp!r}")
    if dest not in DEST:
        raise AsmError(line_no, f"unknown destination {dest!r}")
    if jump not in JUMP:
        raise AsmError(line_no, f"unknown jump {jump!r}")
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def second_pass(instructions, symbols):
    """Translate all A-instructions and C-instructions into 16-bit binary strings."""
    binary = []
    next_var = FIRST_VARIABLE_ADDRESS
    for line_no, text in instructions:
        if text.startswith("("):
            continue
        if text.startswith("@"):
            code, next_var = translate_a(text, line_no, symbols, next_var)
        else:
            code = translate_c(text, line_no)
        binary.append(code)
    return binary


def assemble(asm_path, hack_path):
    """Run both passes on asm_path and write 16-bit binary lines to hack_path."""
    instructions = read_instructions(asm_path)
    symbols, warnings = first_pass(instructions)
    binary = second_pass(instructions, symbols)
    with open(hack_path, "w", encoding="utf-8") as f:
        f.write("\n".join(binary) + "\n")
    return AssembleResult(len(binary), warnings)


# ---------------------------------------------------------------------------
# 4. Command-line entry point
# ---------------------------------------------------------------------------
def main(argv):
    if len(argv) not in (2, 3):
        print("Usage: python assembler.py Prog.asm [Prog.hack]")
        return 2

    asm_path = argv[1]
    hack_path = argv[2] if len(argv) == 3 else os.path.splitext(asm_path)[0] + ".hack"

    if not os.path.exists(asm_path):
        print(f"Error: file not found: {asm_path}")
        return 1

    try:
        result = assemble(asm_path, hack_path)
    except AsmError as err:
        print(err)
        print("No .hack file was written.")
        return 1

    for warning in result.warnings:
        print(warning)

    print(f"OK: {result.count} instructions written to {hack_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
