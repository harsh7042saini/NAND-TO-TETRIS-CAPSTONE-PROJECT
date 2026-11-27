#!/usr/bin/env bash
# Compares assembler.py against the official Nand2Tetris assembler outputs
# and runs the K=92 verification checks via check_assembler.py.
# Run from the capstone folder: bash check_assembler.sh

cd "$(dirname "$0")"
python3 check_assembler.py
