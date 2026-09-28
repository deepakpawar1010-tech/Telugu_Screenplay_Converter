# -*- coding: utf-8 -*-
"""
Screenplay Formatter for Telugu Screenplay Converter
Formats converted screenplay blocks into an industry-standard Tollywood screenplay DOCX document.
Uses Nirmala UI font for high-legibility Telugu Unicode and crisp Latin English rendering.
"""

import os
import io
from typing import List, Tuple, Union
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from screenplay_parser import BlockType, ScreenplayBlock


def set_run_font(run, font_name: str = "Nirmala UI", size_pt: float = 11, bold: bool = False, italic: bool = False, color: RGBColor = None):
    """
    Applies font name, size, bold, italic, and Telugu Unicode complex script font family.
    """
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color

    # Ensure Word's complex script (CS) and East Asian font tags also use Nirmala UI
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)


def create_screenplay_docx(
    converted_blocks: List[Tuple[ScreenplayBlock, str]],
    title: str = "Telugu Screenplay"
) -> Document:
    """
    Creates a python-docx Document formatted according to Tollywood screenplay standards:
    - Page Margins: Left 1.4", Right 1.0", Top 1.0", Bottom 1.0"
    - Nirmala UI font for all elements
    - Scene Headings: Bold, Uppercase, English, flush left
    - Action: Cinematic Telugu, 1.15 line spacing, 6pt space after
    - Character: Bold, Uppercase, English, indented 2.0"
    - Parenthetical: Italic, Telugu acting cue, indented 1.5"
    - Dialogue: Telugu script, indented 1.0" left and 1.0" right
    - Commands / Transitions: Bold, Uppercase, English, right-aligned or indented
    """
    doc = Document()

    # Set page margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.4)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # Base font setup
    style = doc.styles['Normal']
    font = style.font
    font.name = "Nirmala UI"
    font.size = Pt(11)

    for block, converted_text in converted_blocks:
        b_type = block.type
        text = converted_text.strip()
        if not text:
            continue

        p = doc.add_paragraph()
        p_format = p.paragraph_format

        if b_type == BlockType.SCENE_HEADING:
            p_format.left_indent = Inches(0.0)
            p_format.right_indent = Inches(0.0)
            p_format.space_before = Pt(14)
            p_format.space_after = Pt(4)
            p_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text.upper())
            set_run_font(run, font_name="Nirmala UI", size_pt=11.5, bold=True)

        elif b_type == BlockType.ACTION:
            p_format.left_indent = Inches(0.0)
            p_format.right_indent = Inches(0.0)
            p_format.space_before = Pt(2)
            p_format.space_after = Pt(6)
            p_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            set_run_font(run, font_name="Nirmala UI", size_pt=11, bold=False)

        elif b_type == BlockType.CHARACTER:
            p_format.left_indent = Inches(2.0)
            p_format.right_indent = Inches(0.0)
            p_format.space_before = Pt(10)
            p_format.space_after = Pt(1)
            p_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            # Format character name nicely (keep colon if present or standardize)
            char_text = text.upper()
            run = p.add_run(char_text)
            set_run_font(run, font_name="Nirmala UI", size_pt=11, bold=True)

        elif b_type == BlockType.PARENTHETICAL:
            p_format.left_indent = Inches(1.5)
            p_format.right_indent = Inches(1.0)
            p_format.space_before = Pt(0)
            p_format.space_after = Pt(2)
            p_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            set_run_font(run, font_name="Nirmala UI", size_pt=10.5, italic=True)

        elif b_type == BlockType.DIALOGUE:
            p_format.left_indent = Inches(1.0)
            p_format.right_indent = Inches(1.0)
            p_format.space_before = Pt(0)
            p_format.space_after = Pt(6)
            p_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            set_run_font(run, font_name="Nirmala UI", size_pt=11, bold=False)

        elif b_type in (BlockType.SCREENPLAY_COMMAND, BlockType.TRANSITION):
            p_format.left_indent = Inches(0.0)
            p_format.space_before = Pt(10)
            p_format.space_after = Pt(10)
            p_format.line_spacing = 1.0
            # If transition like CUT TO: or FADE OUT, right align
            if any(k in text.upper() for k in ("CUT TO", "FADE OUT", "DISSOLVE TO", "FLASHBACK")):
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text.upper())
            set_run_font(run, font_name="Nirmala UI", size_pt=11, bold=True)

        else:
            # Fallback for general text
            p_format.left_indent = Inches(0.0)
            p_format.space_before = Pt(2)
            p_format.space_after = Pt(4)
            run = p.add_run(text)
            set_run_font(run, font_name="Nirmala UI", size_pt=11)

    return doc


def save_screenplay_docx(
    converted_blocks: List[Tuple[ScreenplayBlock, str]],
    output_destination: Union[str, io.BytesIO],
    title: str = "Telugu Screenplay"
):
    """
    Saves the formatted screenplay to a file path or BytesIO buffer.
    """
    doc = create_screenplay_docx(converted_blocks, title=title)
    doc.save(output_destination)


def export_docx_to_pdf(docx_path: str, pdf_path: str) -> bool:
    """
    Exports a DOCX file to PDF using Microsoft Word automation if available.
    Returns True on success, False if Word COM is unavailable.
    """
    try:
        from docx2pdf import convert
        convert(docx_path, pdf_path)
        return os.path.exists(pdf_path)
    except Exception as e:
        print(f"[PDF Export Notice] Direct Word PDF conversion not available: {e}")
        return False
