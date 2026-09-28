# -*- coding: utf-8 -*-
"""
Screenplay Translator Module
Translates English screenplay action descriptions into natural, contemporary,
cinematic Telugu screenplay prose (Tollywood industry style).
"""

import os
import re
from typing import Optional, List, Tuple
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


def batch_convert_screenplay(
    blocks: List[ScreenplayBlock],
    client=None,
    model_name: str = "gemini-3.5-flash-lite",
    batch_size: int = 18,
    progress_callback=None
) -> List[Tuple[ScreenplayBlock, str]]:
    """
    High-speed batch conversion of screenplay blocks.
    - Instantly resolves headings, characters, parentheticals, and commands (0 API calls).
    - Batches remaining action and dialogue blocks in chunks of 15-20.
    - Yields 10x-20x faster performance than sequential single-block conversion.
    """
    import json
    import time
    
    if client is None:
        from dotenv import load_dotenv
        from google import genai
        project_dir = os.path.dirname(os.path.abspath(__file__))
        load_dotenv(os.path.join(project_dir, ".env"))
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or .env file.")
        client = genai.Client(api_key=api_key)

    total_blocks = len(blocks)
    results = [None] * total_blocks
    api_items = []

    # 1. Instant local resolution pass
    for idx, b in enumerate(blocks):
        clean = b.text.strip()
        btype = b.type

        if btype in (BlockType.SCENE_HEADING, BlockType.CHARACTER, BlockType.SCREENPLAY_COMMAND, BlockType.TRANSITION):
            results[idx] = clean
        elif btype == BlockType.PARENTHETICAL:
            results[idx] = transliterate_parenthetical(clean)
        else:
            # Check if text already consists of Telugu script
            telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', clean))
            alpha_chars = len(re.findall(r'[a-zA-Z\u0C00-\u0C7F]', clean))
            if alpha_chars > 0 and (telugu_chars / alpha_chars) > 0.5:
                results[idx] = clean
            else:
                api_items.append({
                    "id": idx,
                    "type": btype.value,
                    "text": clean
                })

    if progress_callback:
        progress_callback(len(blocks) - len(api_items), total_blocks, f"Resolved {len(blocks) - len(api_items)} screenplay structural elements instantly...")

    # If all blocks were resolved instantly, return immediately!
    if not api_items:
        return [(blocks[i], results[i]) for i in range(total_blocks)]

    # 2. Chunk API items into batches
    chunks = [api_items[i:i + batch_size] for i in range(0, len(api_items), batch_size)]
    completed_api_items = 0

    batch_prompt_template = """You are an expert Telugu Screenplay Writer for Tollywood cinema.
Process the following list of screenplay items:
- For 'ACTION': Translate into natural, contemporary, cinematic Telugu screenplay prose (సినిమా స్క్రీన్‌ప్లే శైలి).
- For 'DIALOGUE': Transliterate into Telugu Unicode script (preserve slang, emotional tone, colloquial expressions; for foreign words like Punjabi/Hindi, phonetically write in Telugu script, do NOT translate meaning).

STRICT RULES:
1. ONLY USE TELUGU UNICODE SCRIPT AND ENGLISH/LATIN CHARACTERS. Do not output any Chinese, Tamil, Devanagari, or other language characters.
2. For age descriptors like (30s) or (45), write (30ల్లో) or (45).
3. Return ONLY a valid JSON array of objects with 'id' and 'converted_text'.

Input items:
"""

    models_to_try = [model_name, "gemini-3.5-flash-lite", "gemini-flash-latest"]
    seen = set()
    models = [m for m in models_to_try if m and not (m in seen or seen.add(m))]

    for c_idx, chunk in enumerate(chunks, 1):
        if progress_callback:
            progress_callback(
                total_blocks - len(api_items) + completed_api_items,
                total_blocks,
                f"Translating batch {c_idx}/{len(chunks)} ({len(chunk)} elements)..."
            )

        payload_json = json.dumps(chunk, ensure_ascii=False)
        full_prompt = batch_prompt_template + payload_json

        batch_success = False
        for m in models:
            for attempt in range(2):
                try:
                    resp = client.models.generate_content(
                        model=m,
                        contents=full_prompt,
                        config={'response_mime_type': 'application/json'}
                    )
                    if resp and resp.text:
                        parsed = json.loads(resp.text)
                        for item in parsed:
                            if "id" in item and "converted_text" in item:
                                results[item["id"]] = item["converted_text"].strip()
                        batch_success = True
                        break
                except Exception as e:
                    time.sleep(2.0 * (attempt + 1))
                    continue
            if batch_success:
                break

        # Fallback to individual block conversion if batch fails
        if not batch_success:
            for item in chunk:
                bid = item["id"]
                results[bid] = convert_block(blocks[bid], client=client, model_name=model_name)

        completed_api_items += len(chunk)

    if progress_callback:
        progress_callback(total_blocks, total_blocks, "Screenplay conversion complete!")

    return [(blocks[i], results[i] if results[i] is not None else blocks[i].text) for i in range(total_blocks)]

