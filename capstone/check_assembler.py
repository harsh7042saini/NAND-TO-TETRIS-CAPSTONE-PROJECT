#!/usr/bin/env python3
"""
check_assembler.py
Automated verification for Harsh Saini's Hack assembler (Roll no. 2501350092, K = 92).
1. Compares Add, Max, Rect, and Pong against official Nand2Tetris .hack outputs.
2. Verifies Box.asm (K = 92: row 92..111, width 16 px / 1 word) assembles cleanly
   and targets Screen offset 2944 (RAM[19328]).
3. Verifies the K mod 3 = 2 extra feature: prints a warning when a label is written twice.
"""
import os
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSEMBLER = os.path.join(SCRIPT_DIR, "assembler.py")

official_programs = ["Add", "Max", "Rect", "Pong"]
all_passed = True

with tempfile.TemporaryDirectory() as tmp_dir:
    # 1. Compare official Nand2Tetris benchmark outputs
    for prog in official_programs:
        src = os.path.join(SCRIPT_DIR, "asm_tests", f"{prog}.asm")
        official = os.path.join(SCRIPT_DIR, "asm_tests", "official", f"{prog}.hack")
        out_hack = os.path.join(tmp_dir, f"{prog}.hack")

        proc = subprocess.run([sys.executable, ASSEMBLER, src, out_hack],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            print(f"[FAIL] {prog}.asm failed to assemble:\n{proc.stderr or proc.stdout}")
            all_passed = False
            continue

        with open(official, "r", encoding="utf-8") as f:
            official_lines = [line.strip() for line in f if line.strip()]
        with open(out_hack, "r", encoding="utf-8") as f:
            generated_lines = [line.strip() for line in f if line.strip()]

        if official_lines == generated_lines:
            print(f"[PASS] {prog}.asm -> matches official output ({len(generated_lines)} lines)")
        else:
            print(f"[FAIL] {prog}.asm -> differs from official output "
                  f"(expected {len(official_lines)}, got {len(generated_lines)})")
            all_passed = False

    # 2. Verify Box.asm for K = 92 (offset 2944 = 32*92, height 20, width 1 word)
    box_src = os.path.join(SCRIPT_DIR, "Box.asm")
    box_out = os.path.join(tmp_dir, "Box.hack")
    proc_box = subprocess.run([sys.executable, ASSEMBLER, box_src, box_out],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc_box.returncode != 0 or "Warning" in proc_box.stdout:
        print(f"[FAIL] Box.asm assembly unexpected status/warning:\n{proc_box.stdout}\n{proc_box.stderr}")
        all_passed = False
    else:
        with open(box_out, "r", encoding="utf-8") as f:
            box_lines = [line.strip() for line in f if line.strip()]
        expected_offset_bin = "0" + format(2944, "015b")  # @2944 -> 32 * 92
        expected_height_bin = "0" + format(20, "015b")    # @20   -> 20 rows
        expected_width_bin = "0" + format(1, "015b")      # @1    -> (92 mod 4) + 1 = 1 word
        if (len(box_lines) == 47
                and box_lines[10] == expected_offset_bin
                and box_lines[14] == expected_height_bin
                and box_lines[22] == expected_width_bin):
            print(f"[PASS] Box.asm (K=92) -> {len(box_lines)} instructions, "
                  f"offset @2944, height @20, width @1 verified")
        else:
            print("[FAIL] Box.asm generated unexpected instruction sequence.")
            all_passed = False

    # 3. Verify K mod 3 = 2 duplicate-label warning feature
    dup_src = os.path.join(SCRIPT_DIR, "asm_tests", "DuplicateLabel.asm")
    dup_out = os.path.join(tmp_dir, "DuplicateLabel.hack")
    proc_dup = subprocess.run([sys.executable, ASSEMBLER, dup_src, dup_out],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc_dup.returncode == 0 and "Warning" in proc_dup.stdout and "LOOP" in proc_dup.stdout:
        print("[PASS] DuplicateLabel.asm -> K mod 3 = 2 warning printed cleanly without crashing")
    else:
        print(f"[FAIL] DuplicateLabel.asm did not emit expected warning:\n{proc_dup.stdout}\n{proc_dup.stderr}")
        all_passed = False

if all_passed:
    print("\nAll assembler verification tests passed successfully!")
    sys.exit(0)
else:
    print("\nSome tests failed.")
    sys.exit(1)
