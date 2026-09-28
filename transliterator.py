# -*- coding: utf-8 -*-
"""
Screenplay Transliterator Module
Handles:
1. Roman Telugu Dialogue -> Telugu Unicode Script (NOT translation, preserves slang/voice)
2. Other language dialogue (Roman Punjabi/Hindi) -> Telugu Script representation of sound (NOT meaning)
3. Parentheticals -> Standard Telugu Screenplay directions
"""

import os
import re
from typing import Optional

# Standard Screenplay Parentheticals Map
COMMON_PARENTHETICALS = {
    "in hindi": "(హిందీలో)",
    "in punjabi": "(పంజాబీలో)",
    "in english": "(ఇంగ్లీషులో)",
    "to himself": "(తనలో తాను)",
    "to herself": "(తనలో తాను)",
    "confused": "(అయోమయంగా)",
    "in shock": "(షాక్‌తో)",
    "shocked": "(ఆశ్చర్యంతో)",
    "smiling": "(చిరునవ్వుతో)",
    "smiling softly": "(నెమ్మదిగా నవ్వుతూ)",
    "laughing": "(నవ్వుతూ)",
    "laughs loudly and shouts": "(బిగ్గరగా నవ్వుతూ అరుస్తూ)",
    "crying, frantic": "(ఏడుస్తూ, కంగారుగా)",
    "in tears": "(కన్నీళ్లతో)",
    "whispering": "(గుసగుసలాడుతూ)",
    "whispering anxiously": "(ఆందోళనగా గుసగుసలాడుతూ)",
    "panicked": "(తీవ్రమైన కంగారులో)",
    "gesturing to clarify": "(సైగలతో వివరిస్తూ)",
    "soft prayer": "(చిన్నగా ప్రార్థన చేస్తూ)",
    "beat": "(క్షణిక విరామం)",
}

TRANSLITERATION_PROMPT = """You are an expert Telugu script transliterator for cinema screenplays.
TASK: Convert the following Romanized dialogue into TELUGU UNICODE SCRIPT.

STRICT RULES:
1. THIS IS TRANSLITERATION, NOT TRANSLATION.
2. If the dialogue is Romanized Telugu (e.g. "Em chepali veediki... TU SUNDAR... MANCHODIVI... AACHA... TEA ICHAV!"), render it directly in spoken Telugu Unicode script. Preserve colloquial slang, emotion, character voice, repetitions, and punctuation. Do NOT formalize it.
3. If the dialogue is Romanized Punjabi, Hindi, or another language (e.g. "Khush kar dita paaji? Kithon aajya rahe ho?"), DO NOT translate its meaning into Telugu! Only convert the exact pronunciation sounds into Telugu script (e.g. "ఖుష్ కర్ దితా పాజీ? కిత్థోం ఆజ్యా రహే హో?").
4. Output ONLY the Telugu script dialogue. Do NOT add notes, quotes, or explanations."""


def transliterate_parenthetical(text: str) -> str:
    """
    Converts English screenplay parentheticals to Telugu screenplay conventions.
    """
    clean = text.strip()
    if clean.startswith('(') and clean.endswith(')'):
        inner = clean[1:-1].strip().lower()
        if inner in COMMON_PARENTHETICALS:
            return COMMON_PARENTHETICALS[inner]
        for k, v in COMMON_PARENTHETICALS.items():
            if k in inner:
                return v
        return f"({inner})"
    return clean


def transliterate_dialogue(text: str, client=None, model_name: str = "gemini-flash-lite-latest") -> str:
    """
    Converts Romanized Telugu or Romanized Punjabi/Hindi dialogue into Telugu Unicode script.
    Preserves voice, slang, sound, and emotional nuance without translating foreign words.
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
        # Load from project directory .env
        project_dir = os.path.dirname(os.path.abspath(__file__))
        load_dotenv(os.path.join(project_dir, ".env"))
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or .env file.")
        client = genai.Client(api_key=api_key)

    prompt = f"{TRANSLITERATION_PROMPT}\n\nRomanized Dialogue:\n{clean_text}"

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
            
    raise RuntimeError(f"Transliteration failed across models: {last_err}")
