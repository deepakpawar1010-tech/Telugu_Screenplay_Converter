# -*- coding: utf-8 -*-
"""
Screenplay Translator Module
Translates English screenplay action descriptions into natural, contemporary,
cinematic Telugu screenplay prose (Tollywood industry style).
"""

import os
import re
from typing import Optional
from screenplay_parser import BlockType, ScreenplayBlock
from transliterator import transliterate_dialogue, transliterate_parenthetical

ACTION_TRANSLATION_PROMPT = """You are an experienced Telugu Cinema (Tollywood) Screenplay Writer.
TASK: Translate the following English screenplay ACTION DESCRIPTION into natural, contemporary, cinematic Telugu screenplay language.

CRITICAL SCREENPLAY RULES:
1. NATURAL CINEMATIC TELUGU: Write in the visual, engaging style used by modern Telugu directors and screenwriters (సినిమా స్క్రీన్‌ప్లే శైలి).
2. DO NOT DO LITERAL / TEXTBOOK TRANSLATION: Capture the visual atmosphere, camera intent, and character actions fluidly.
   Example:
   Input: "Dense fog covers the highway. A motorcycle cuts through the mist and stops at a roadside dhaba."
   Desired Style: "దట్టమైన పొగమంచు హైవేను కమ్మేసింది. పొగమంచును చీల్చుకుంటూ ఒక మోటార్సైకిల్ వచ్చి రోడ్డుపక్కన ఉన్న ధాబా దగ్గర ఆగుతుంది."
3. STRICT FIDELITY:
   - Preserve meaning, characters, actions, sequence, and cinematic intent.
   - Do NOT add new information or embellishments.
   - Do NOT remove any actions or details.
   - Do NOT invent dialogue.
   - Do NOT make the Telugu overly archaic, pedantic, or bookish (గ్రాంథికం వద్దు, సహజమైన సినిమాటిక్ శైలి ఉండాలి).
4. Output ONLY the translated Telugu screenplay prose. Do NOT add notes or English commentary."""


def translate_action(text: str, client=None, model_name: str = "gemini-flash-latest") -> str:
    """
    Translates an English screenplay action description into cinematic Telugu.
    """
    clean_text = text.strip()
    if not clean_text:
        return ""

    # If the text is already mostly Telugu script, preserve it as-is
    telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', clean_text))
    alpha_chars = len(re.findall(r'[a-zA-Z\u0C00-\u0C7F]', clean_text))
    if alpha_chars > 0 and (telugu_chars / alpha_chars) > 0.5:
        return clean_text
        
    if client is None:
        from dotenv import load_dotenv
        from google import genai
        project_dir = os.path.dirname(os.path.abspath(__file__))
        load_dotenv(os.path.join(project_dir, ".env"))
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or .env file.")
        client = genai.Client(api_key=api_key)

    prompt = f"{ACTION_TRANSLATION_PROMPT}\n\nEnglish Action Description:\n{clean_text}"

    candidates = [model_name, "gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3-flash-preview"]
    seen = set()
    models_to_try = [m for m in candidates if m and not (m in seen or seen.add(m))]
    last_err = None
    import time
    for m in models_to_try:
        for attempt in range(2):
            try:
                resp = client.models.generate_content(
                    model=m,
                    contents=prompt
                )
                if resp and resp.text:
                    return resp.text.strip()
            except Exception as e:
                last_err = e
                time.sleep(2.0 * (attempt + 1))
                continue
            
    raise RuntimeError(f"Action translation failed across models: {last_err}")


def convert_block(block: ScreenplayBlock, client=None, model_name: str = "gemini-flash-lite-latest") -> str:
    """
    Routes a ScreenplayBlock to the appropriate operation based on its BlockType:
    - SCENE_HEADING: Preserved as-is (English)
    - CHARACTER: Preserved as-is (English)
    - SCREENPLAY_COMMAND / TRANSITION: Preserved as-is (English)
    - PARENTHETICAL: Transliterated / mapped to Telugu acting directions
    - DIALOGUE: Transliterated to Telugu Unicode script (voice/slang preserved)
    - ACTION: Translated into cinematic Telugu screenplay prose
    """
    btype = block.type
    raw_text = block.text.strip()
    
    # Preserve elements
    if btype in (BlockType.SCENE_HEADING, BlockType.CHARACTER, BlockType.SCREENPLAY_COMMAND, BlockType.TRANSITION):
        return raw_text
        
    if btype == BlockType.PARENTHETICAL:
        return transliterate_parenthetical(raw_text)
        
    if btype == BlockType.DIALOGUE:
        return transliterate_dialogue(raw_text, client=client, model_name=model_name)
        
    if btype == BlockType.ACTION:
        return translate_action(raw_text, client=client, model_name=model_name)
        
    return raw_text
