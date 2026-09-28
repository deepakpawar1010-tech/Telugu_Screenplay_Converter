# 🎬 Telugu Screenplay Converter Studio

An AI-powered screenplay translation and formatting platform designed specifically for the **Telugu Film Industry (Tollywood)** standards.

Converts English / Romanized screenplays into industry-standard Tollywood screenplay format with natural cinematic Telugu action descriptions, authentic Telugu-script dialogues, and properly preserved English sluglines and character cues.

---

## 🌟 Features

- **⚡ 50:50 Live Split Screenwriter**: Type English screenplay on the left; get real-time Tollywood Telugu formatting on the right.
- **📁 Universal Script Converter**: Ingest full `.docx`, `.pdf`, or `.txt` screenplay documents with element breakdown and progress tracking.
- **📜 Tollywood Formatting Standards**:
  - **Scene Headings**: UPPERCASE English (`EXT. HIGHWAY - 4:20 AM`)
  - **Character Headers**: UPPERCASE English (`SATYA:`, `PARTHA:`)
  - **Action Lines**: Visual, contemporary, cinematic Telugu screenplay prose (సినిమా స్క్రీన్‌ప్లే శైలి)
  - **Dialogues**: Transliterated directly into Telugu script preserving tone, humor, and colloquial nuances
  - **Foreign / Regional Dialogues**: Punjabi, Hindi, or English lines phonetically represented in Telugu script without translation
  - **Screenplay Commands & Transitions**: English (`FADE OUT.`, `CUT TO:`)
- **📄 Industry-Standard .DOCX Export**:
  - Formatted using `Nirmala UI` font for crisp Telugu Unicode rendering
  - 1.4" Left binding margin, 1.0" Right/Top/Bottom margins
  - Accurate character (2.0"), parenthetical (1.5"), and dialogue (1.0") indentations
- **🎨 Cinematic Studio UI**:
  - Dark Obsidian (Cinema) and Classic Ivory (Manuscript) themes
  - One-click template snippets (`+ Scene Heading`, `+ Action`, `+ Dialogue`, `+ Transition`)

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/deepakpawar1010-tech/Telugu_Screenplay_Converter.git
cd Telugu_Screenplay_Converter
```

### 2. Set up virtual environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Create a `.env` file in the project root:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/))*

### 5. Launch the Studio
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 📁 Project Architecture

```text
Telugu_Screenplay_Converter/
├── app.py                  # Streamlit Studio application & UI
├── extractor.py            # Extracts text & blocks from DOCX and PDF
├── screenplay_parser.py    # Classifies text into screenplay element blocks
├── translator.py           # Cinematic Telugu action translation via Gemini API
├── transliterator.py       # Dialogue & parenthetical transliteration
├── formatter.py            # Formats standard Tollywood .DOCX documents
├── quality_checker.py      # Automated validation & screenplay quality checks
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment configuration template
├── .gitignore              # Git ignore rules (protects API keys & venvs)
└── tests/
    ├── sample_screenplay.txt
    └── test_conversion.py  # End-to-end verification test suite
```

---

## 🧪 Testing

Run the automated 9-block verification test suite:
```bash
python tests/test_conversion.py
```

---

## 📄 License
MIT License
