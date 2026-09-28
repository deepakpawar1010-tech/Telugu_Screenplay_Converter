# -*- coding: utf-8 -*-
"""
Screenplay Parser
Classifies screenplay text into semantic blocks:
- SCENE_HEADING
- ACTION
- CHARACTER
- PARENTHETICAL
- DIALOGUE
- SCREENPLAY_COMMAND
- TRANSITION
- OTHER
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any


class BlockType(Enum):
    SCENE_HEADING = "SCENE_HEADING"
    ACTION = "ACTION"
    CHARACTER = "CHARACTER"
    PARENTHETICAL = "PARENTHETICAL"
    DIALOGUE = "DIALOGUE"
    SCREENPLAY_COMMAND = "SCREENPLAY_COMMAND"
    TRANSITION = "TRANSITION"
    OTHER = "OTHER"


@dataclass
class ScreenplayBlock:
    type: BlockType
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"<ScreenplayBlock type={self.type.value} text={self.text[:40]!r}>"


HEADING_PATTERN = re.compile(
    r'^(SCENE\b|ACT\b|EXT[\.\s]|INT[\.\s]|EXTERIOR\b|INTERIOR\b)',
    re.IGNORECASE
)

COMMAND_PATTERN = re.compile(
    r'^(FADE\s+IN:?|FADE\s+OUT\.?|CUT\s+TO:?|DISSOLVE\s+TO:?|FLASHBACK\s+CUT\s+TO:?|BACK\s+TO\s+SCENE:?|THE\s+END\.?)$',
    re.IGNORECASE
)

CHARACTER_PATTERN = re.compile(
    r'^[A-Z0-9\s\(\)\.\/\'\-]{2,35}:$'
)

PARENTHETICAL_PATTERN = re.compile(
    r'^\([^\)]+\)$'
)


def parse_screenplay_text(raw_text: str) -> List[ScreenplayBlock]:
    """
    Parses screenplay text (paragraphs separated by blank lines or line breaks)
    into classified ScreenplayBlock objects.
    """
    # Normalize line endings
    normalized = raw_text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Split by blank lines or multi-newlines into paragraph chunks
    raw_chunks = re.split(r'\n\s*\n', normalized)
    
    blocks: List[ScreenplayBlock] = []
    expecting_dialogue = False
    current_character = None
    
    for chunk in raw_chunks:
        lines = [l.strip() for l in chunk.split('\n') if l.strip()]
        if not lines:
            continue
            
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check 1: Screenplay command / Transition
            if COMMAND_PATTERN.match(line):
                blocks.append(ScreenplayBlock(type=BlockType.SCREENPLAY_COMMAND, text=line))
                expecting_dialogue = False
                current_character = None
                i += 1
                continue
                
            # Check 2: Scene Heading
            if HEADING_PATTERN.match(line):
                blocks.append(ScreenplayBlock(type=BlockType.SCENE_HEADING, text=line))
                expecting_dialogue = False
                current_character = None
                i += 1
                continue
                
            # Check 3: Character Cue (e.g. "SATYA:" or "SATYA" followed by parenthetical/dialogue)
            is_char_cue = bool(CHARACTER_PATTERN.match(line))
            if not is_char_cue and line.isupper() and len(line) <= 30 and not line.endswith(('.', '?', '!')):
                # Look ahead: if next line is parenthetical or text, might be character cue without colon
                if i + 1 < len(lines) and (PARENTHETICAL_PATTERN.match(lines[i + 1]) or not lines[i + 1].isupper()):
                    is_char_cue = True
                    if not line.endswith(':'):
                        line = line + ":"
                        
            if is_char_cue:
                current_character = line.rstrip(':').strip()
                blocks.append(ScreenplayBlock(
                    type=BlockType.CHARACTER,
                    text=line,
                    metadata={"character": current_character}
                ))
                expecting_dialogue = True
                i += 1
                continue
                
            # Check 4: Parenthetical
            if PARENTHETICAL_PATTERN.match(line):
                blocks.append(ScreenplayBlock(
                    type=BlockType.PARENTHETICAL,
                    text=line,
                    metadata={"character": current_character}
                ))
                expecting_dialogue = True
                i += 1
                continue
                
            # Check 5: Dialogue or Action
            if expecting_dialogue:
                # Group contiguous lines as dialogue
                dialogue_lines = [line]
                i += 1
                while i < len(lines):
                    next_l = lines[i]
                    if (HEADING_PATTERN.match(next_l) or 
                        COMMAND_PATTERN.match(next_l) or 
                        CHARACTER_PATTERN.match(next_l) or 
                        PARENTHETICAL_PATTERN.match(next_l)):
                        break
                    dialogue_lines.append(next_l)
                    i += 1
                    
                blocks.append(ScreenplayBlock(
                    type=BlockType.DIALOGUE,
                    text=" ".join(dialogue_lines),
                    metadata={"character": current_character}
                ))
                expecting_dialogue = False
            else:
                # Group contiguous lines as Action description
                action_lines = [line]
                i += 1
                while i < len(lines):
                    next_l = lines[i]
                    if (HEADING_PATTERN.match(next_l) or 
                        COMMAND_PATTERN.match(next_l) or 
                        CHARACTER_PATTERN.match(next_l) or 
                        PARENTHETICAL_PATTERN.match(next_l)):
                        break
                    action_lines.append(next_l)
                    i += 1
                    
                blocks.append(ScreenplayBlock(
                    type=BlockType.ACTION,
                    text=" ".join(action_lines)
                ))
                expecting_dialogue = False
                current_character = None
                
    return blocks
