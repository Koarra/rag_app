# Document Processing Pipeline

Simple pipeline for analyzing documents for entities and financial crime risks.

## Quick Start

```bash
# Install dependencies
pip install openai python-docx PyPDF2

# For OCR support on scanned PDFs (optional)
pip install pdf2image pytesseract
# System dependencies: sudo apt-get install tesseract-ocr poppler-utils

# Run the pipeline
python run_pipeline.py document.pdf

# Or with entity grouping (deduplication)
python run_pipeline.py document.pdf --group-entities
```

## Files

- **step1_summarize.py** - Extract text (with OCR) and summarize
- **step2_extract_entities.py** - Extract persons and companies
- **step3_describe_entities.py** - Describe each entity
- **step4_analyze_risks.py** - Flag entities for money laundering & sanctions evasion
- **step5_group_entities.py** - Group similar entities (optional deduplication)
- **run_pipeline.py** - Run all steps automatically

## Usage

### Option 1: Run all steps at once
```bash
python run_pipeline.py contract.pdf

# With entity grouping/deduplication
python run_pipeline.py contract.pdf --group-entities
```

### Option 2: Run steps individually
```bash
python step1_summarize.py contract.pdf
python step2_extract_entities.py
python step3_describe_entities.py
python step4_analyze_risks.py
python step5_group_entities.py  # Optional
```

## What It Does

### Step 1: Extract & Summarize
- Extracts text from PDF or DOCX
- Uses OCR for scanned PDFs (if available)
- Generates comprehensive summary
- **Output:** `extracted_text.txt`, `summary.json`

### Step 2: Extract Entities
- Identifies all persons mentioned
- Identifies all companies/organizations
- **Output:** `entities.json`

### Step 3: Describe Entities
- Creates detailed profile for each entity
- Extracts: role, activities, related entities, financial details
- **Output:** `entity_descriptions.json`

### Step 4: Analyze Risks
- Analyzes document for money laundering indicators
- Analyzes document for sanctions evasion indicators
- Flags specific entities with evidence
- **Output:** `risk_assessment.json`

### Step 5: Group Entities (Optional)
- Identifies duplicate/similar entities
- Groups variations of the same entity (e.g., "John Smith", "Mr. Smith", "J. Smith")
- Merges entity descriptions
- **Output:** `grouped_entities.json`
- **Use case:** When you have many entity variations referring to the same person/company

## OCR Support

**For scanned PDFs**, install OCR dependencies:

```bash
# Python packages
pip install pdf2image pytesseract

# System dependencies
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr poppler-utils

# macOS:
brew install tesseract poppler

# Windows:
# Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# Download Poppler: https://github.com/oschwartz10612/poppler-windows/releases
```

The scripts will automatically detect if OCR is available and use it when needed.

## Output Files

After processing, you'll have:

```
extracted_text.txt        - Raw document text
summary.json              - Document summary
entities.json             - {"persons": [...], "companies": [...]}
entity_descriptions.json  - Detailed entity profiles
risk_assessment.json      - Risk analysis with flagged entities
grouped_entities.json     - Deduplicated entities (if step 5 run)
```

## Features

✅ **Simple** - One script per step, no complex structure
✅ **Standalone** - Each script is independent, no imports between them
✅ **OCR Support** - Handles scanned PDFs automatically
✅ **Flexible** - Run all steps or individual steps
✅ **Clear Output** - JSON files for easy processing

## Cost

Approximately **$0.15-0.30** per document in OpenAI API fees.

## Example

```bash
$ python run_pipeline.py contract.pdf
Enter your OpenAI API key: sk-...

============================================================
DOCUMENT PROCESSING PIPELINE
============================================================
Input file: contract.pdf

This will run 4 steps:
1. Extract text and summarize
2. Extract entities (persons & companies)
3. Describe each entity
4. Analyze risks (money laundering & sanctions evasion)
============================================================

============================================================
Running step1_summarize.py...
============================================================

=== STEP 1: SUMMARIZE DOCUMENT ===
Processing: contract.pdf
Extracting text...
Extracted 12,543 characters
Saved: extracted_text.txt
Generating summary...
Saved: summary.json

✓ step1_summarize.py completed successfully

[... steps 2, 3, 4 ...]

============================================================
ALL STEPS COMPLETE!
============================================================

Generated files:
  - extracted_text.txt
  - summary.json
  - entities.json
  - entity_descriptions.json
  - risk_assessment.json
```

## Requirements

```
openai>=1.12.0
python-docx>=1.1.0
PyPDF2>=3.0.0

# Optional for OCR:
pdf2image>=1.16.3
pytesseract>=0.3.10
Pillow>=10.0.0
```
