# -*- coding: utf-8 -*-
"""
Screenplay Quality Checker Module
Performs structural, fidelity, and script validation on converted screenplay blocks:
- Missing or empty blocks
- Accidental translation of headings, character cues, commands
- English text accidentally remaining in action or dialogue
- Verification of Telugu script presence
"""

import re
from typing import List, Dict, Any
from screenplay_parser import BlockType, ScreenplayBlock

TELUGU_UNICODE_RE = re.compile(r'[\u0C00-\u0C7F]')
ENGLISH_WORD_RE = re.compile(r'[a-zA-Z]{3,}')


class ScreenplayQualityChecker:
    """
    Validates conversion quality block by block and across the entire screenplay.
    """

    def check_block(self, original: ScreenplayBlock, converted: str) -> List[str]:
        warnings = []
        orig_text = original.text.strip()
        conv_text = converted.strip()

        # 1. Empty check
        if not conv_text:
            warnings.append("EMPTY_OUTPUT: Converted text is empty.")
            return warnings

        # 2. Scene Heading Preservation
        if original.type == BlockType.SCENE_HEADING:
            if conv_text.upper() != orig_text.upper():
                warnings.append(f"HEADING_MODIFIED: Heading was altered (Expected: {orig_text!r}, Got: {conv_text!r})")

        # 3. Character Cue Preservation
        elif original.type == BlockType.CHARACTER:
            orig_char = orig_text.rstrip(':').strip().upper()
            conv_char = conv_text.rstrip(':').strip().upper()
            if orig_char != conv_char:
                warnings.append(f"CHARACTER_MODIFIED: Character name altered (Expected: {orig_char!r}, Got: {conv_char!r})")

        # 4. Screenplay Command / Transition Preservation
        elif original.type in (BlockType.SCREENPLAY_COMMAND, BlockType.TRANSITION):
            if conv_text.upper().rstrip('.') != orig_text.upper().rstrip('.'):
                warnings.append(f"COMMAND_MODIFIED: Screenplay command altered (Expected: {orig_text!r}, Got: {conv_text!r})")

        # 5. Parenthetical Check
        elif original.type == BlockType.PARENTHETICAL:
            if not (conv_text.startswith('(') and conv_text.endswith(')')):
                warnings.append("PARENTHETICAL_FORMAT: Missing enclosing parentheses.")
            if not TELUGU_UNICODE_RE.search(conv_text):
                warnings.append("PARENTHETICAL_NO_TELUGU: Parenthetical does not contain Telugu script.")

        # 6. Action Description Translation Check
        elif original.type == BlockType.ACTION:
            if not TELUGU_UNICODE_RE.search(conv_text):
                warnings.append("ACTION_NO_TELUGU: Action description does not contain Telugu characters.")
            else:
                # Check for significant remaining English (e.g. untranslated paragraphs)
                eng_words = ENGLISH_WORD_RE.findall(conv_text)
                # Filter out standard character names or bike models like Royal Enfield
                filtered_eng = [w for w in eng_words if w.upper() not in ('SATYA', 'PARTHA', 'KAMALA', 'CHANDRA', 'ANIRUDH', 'SAILAJA', 'ENFIELD')]
                if len(filtered_eng) > 6:
                    warnings.append(f"ACTION_LEFTOVER_ENGLISH: Action has many untranslated English words ({filtered_eng[:5]}...)")

        # 7. Dialogue Transliteration Check
        elif original.type == BlockType.DIALOGUE:
            if not TELUGU_UNICODE_RE.search(conv_text):
                warnings.append("DIALOGUE_NO_TELUGU: Dialogue does not contain Telugu Unicode script.")

        return warnings

    def validate_screenplay(self, original_blocks: List[ScreenplayBlock], converted_texts: List[str]) -> Dict[str, Any]:
        """
        Validates the complete converted screenplay.
        """
        if len(original_blocks) != len(converted_texts):
            return {
                "passed": False,
                "error": f"BLOCK_COUNT_MISMATCH: Input had {len(original_blocks)} blocks, output has {len(converted_texts)} blocks."
            }

        all_warnings = []
        for i, (orig, conv) in enumerate(zip(original_blocks, converted_texts)):
            w = self.check_block(orig, conv)
            if w:
                all_warnings.append({"index": i, "block_type": orig.type.value, "warnings": w, "original": orig.text, "converted": conv})

        return {
            "passed": len(all_warnings) == 0,
            "total_blocks": len(original_blocks),
            "warning_count": len(all_warnings),
            "issues": all_warnings
        }
