# Simple Document Processing Pipeline

One script per step. Each script is completely standalone.

## Files

- **step1_summarize.py** - Extract text and generate summary
- **step2_extract_entities.py** - Extract persons and companies
- **step3_describe_entities.py** - Generate entity descriptions
- **step4_analyze_risks.py** - Flag entities for crimes
- **run_pipeline.py** - Run all steps automatically

## Quick Start

### Run all steps at once:
```bash
python run_pipeline.py document.pdf
```

### Or run steps individually:
```bash
# Step 1: Extract and summarize
python step1_summarize.py document.pdf

# Step 2: Extract entities
python step2_extract_entities.py

# Step 3: Describe entities
python step3_describe_entities.py

# Step 4: Analyze risks
python step4_analyze_risks.py
```

## What Each Step Does

### Step 1: `step1_summarize.py`
- Reads PDF or DOCX file
- Extracts all text
- Generates summary using OpenAI
- **Creates:** `extracted_text.txt`, `summary.json`

### Step 2: `step2_extract_entities.py`
- Reads `extracted_text.txt`
- Extracts all persons and companies
- **Creates:** `entities.json`

### Step 3: `step3_describe_entities.py`
- Reads `extracted_text.txt` and `entities.json`
- Generates detailed description for each entity
- Includes: role, activities, related entities, financial details
- **Creates:** `entity_descriptions.json`

### Step 4: `step4_analyze_risks.py`
- Reads `extracted_text.txt` and `entity_descriptions.json`
- Analyzes document for money laundering and sanctions evasion
- Flags specific entities with evidence
- **Creates:** `risk_assessment.json`

## Output Files

All results are saved as JSON files:

```
extracted_text.txt        - Raw extracted document text
summary.json              - Document summary
entities.json             - List of persons and companies
entity_descriptions.json  - Detailed entity profiles
risk_assessment.json      - Risk analysis with flagged entities
```

## Requirements

```bash
pip install openai python-docx PyPDF2
```

## Example Usage

```bash
# Process a contract
python run_pipeline.py contract.pdf

# Process an agreement
python run_pipeline.py sales_agreement.docx

# Run only step 4 (assumes previous steps completed)
python step4_analyze_risks.py
```

## Features

✅ Simple - one script per step
✅ Standalone - no imports between scripts
✅ Clear output - JSON files for each step
✅ Flexible - run all at once or step by step
✅ Readable - simple Python code, no classes

## Cost

Approximately $0.15-0.30 per document in OpenAI API fees.
