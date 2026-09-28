# -*- coding: utf-8 -*-
"""
End-to-End Conversion and Quality Test Suite
Tests screenplay block parsing, action translation, dialogue transliteration,
parentheticals, and structural preservation.
"""

import os
import sys
import io

# Ensure UTF-8 output on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_DIR)

from dotenv import load_dotenv
from google import genai

from screenplay_parser import parse_screenplay_text, BlockType, ScreenplayBlock
from translator import convert_block, translate_action
from transliterator import transliterate_dialogue, transliterate_parenthetical
from quality_checker import ScreenplayQualityChecker

def run_sample_screenplay_test():
    print("=" * 70)
    print("TELUGU SCREENPLAY CONVERSION ENGINE: VERIFICATION TEST")
    print("=" * 70)

    # 1. Load .env
    env_path = os.path.join(PROJECT_DIR, ".env")
    load_dotenv(env_path)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY not found in .env file!")
        return False
        
    client = genai.Client(api_key=api_key)

    # 2. Read sample input file
    sample_file = os.path.join(PROJECT_DIR, "tests", "sample_screenplay.txt")
    with open(sample_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    print("\n>>> STEP 1: PARSING SCREENPLAY BLOCKS...")
    blocks = parse_screenplay_text(raw_text)
    print(f"Total blocks detected: {len(blocks)}\n")

    # 3. Convert blocks and check quality
    checker = ScreenplayQualityChecker()
    converted_blocks = []
    
    print(">>> STEP 2: CONVERTING BLOCKS & RUNNING QUALITY CHECKS...\n")
    print("-" * 70)

    for i, b in enumerate(blocks, 1):
        # Convert
        converted = convert_block(b, client=client)
        converted_blocks.append(converted)
        
        # Check
        warnings = checker.check_block(b, converted)

        # Display block report
        print(f"BLOCK #{i}")
        print(f"  1. Original Block : {b.text!r}")
        print(f"  2. Detected Type  : {b.type.value}")
        print(f"  3. Converted Result:\n     {converted}")
        if warnings:
            print(f"  4. Warnings       : {warnings}")
        else:
            print(f"  4. Warnings       : None (Passed)")
        print("-" * 70)

    # 4. Specific Requirement Verification Tests
    print("\n>>> STEP 3: RUNNING INDIVIDUAL MILESTONE TESTS...")
    results = {}

    # TEST 1: English action description
    action_block = next((b for b in blocks if b.type == BlockType.ACTION), None)
    action_idx = blocks.index(action_block) if action_block else -1
    conv_action = converted_blocks[action_idx] if action_idx >= 0 else ""
    t1_pass = bool(conv_action and any('\u0C00' <= c <= '\u0C7F' for c in conv_action))
    results["TEST 1 (English Action -> Natural Cinematic Telugu)"] = (t1_pass, conv_action)

    # TEST 2: Roman Telugu dialogue
    # Em chepali veediki...
    tel_dialogue = next((converted_blocks[i] for i, b in enumerate(blocks) if b.type == BlockType.DIALOGUE and "Em chepali" in b.text), "")
    t2_pass = bool(tel_dialogue and any('\u0C00' <= c <= '\u0C7F' for c in tel_dialogue))
    results["TEST 2 (Roman Telugu Dialogue -> Telugu Script)"] = (t2_pass, tel_dialogue)

    # TEST 3: Roman Punjabi dialogue
    # Khush kar dita paaji?
    pun_dialogue = next((converted_blocks[i] for i, b in enumerate(blocks) if b.type == BlockType.DIALOGUE and "Khush kar" in b.text), "")
    # Check that Punjabi sounds are kept in Telugu script without translating to Telugu meaning (like "సంతోషపడ్డావా")
    t3_pass = bool(pun_dialogue and any('\u0C00' <= c <= '\u0C7F' for c in pun_dialogue) and ("ఖుష్" in pun_dialogue or "పాజీ" in pun_dialogue or "కిత్" in pun_dialogue or "రహే" in pun_dialogue))
    results["TEST 3 (Roman Punjabi Dialogue -> Telugu Script Transliteration)"] = (t3_pass, pun_dialogue)

    # TEST 4: Parentheticals
    parens = [(b.text, converted_blocks[i]) for i, b in enumerate(blocks) if b.type == BlockType.PARENTHETICAL]
    t4_pass = bool(parens and all(p[1].startswith('(') and p[1].endswith(')') and any('\u0C00' <= c <= '\u0C7F' for c in p[1]) for p in parens))
    results["TEST 4 (Parentheticals -> Telugu Screenplay Directions)"] = (t4_pass, parens)

    # TEST 5: Screenplay heading preservation
    heading = next((converted_blocks[i] for i, b in enumerate(blocks) if b.type == BlockType.SCENE_HEADING), "")
    t5_pass = (heading.strip().upper() == "EXT. HIGHWAY - 4:20 AM")
    results["TEST 5 (Screenplay Heading Preserved as-is)"] = (t5_pass, heading)

    # TEST 6: Character name preservation
    characters = [converted_blocks[i] for i, b in enumerate(blocks) if b.type == BlockType.CHARACTER]
    t6_pass = ("SATYA:" in characters and "PARTHA:" in characters)
    results["TEST 6 (Character Names Preserved: SATYA:, PARTHA:)"] = (t6_pass, characters)

    # TEST 7: FADE OUT / CUT TO preservation
    command = next((converted_blocks[i] for i, b in enumerate(blocks) if b.type == BlockType.SCREENPLAY_COMMAND), "")
    t7_pass = (command.strip().upper() == "FADE OUT.")
    results["TEST 7 (FADE OUT. Command Preserved)"] = (t7_pass, command)

    for test_name, (passed, details) in results.items():
        status = "PASSED [OK]" if passed else "FAILED [X]"
        print(f"  * {test_name}: {status}")
        if not passed:
            print(f"      Detail: {details}")

    # Overall Summary
    validation = checker.validate_screenplay(blocks, converted_blocks)
    all_passed = all(r[0] for r in results.values()) and validation["passed"]

    print("\n" + "=" * 70)
    print(f"TEST SUITE RESULT: {'ALL TESTS PASSED SUCCESSFULLY!' if all_passed else 'SOME WARNINGS/CHECKS FAILED'}")
    print("=" * 70)

    return all_passed

if __name__ == "__main__":
    run_sample_screenplay_test()
