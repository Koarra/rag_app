# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install system dependencies for OCR
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr poppler-utils

# macOS:
brew install tesseract poppler
```

### 2. Configure API Key
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env
```

Or set as environment variable:
```bash
export OPENAI_API_KEY=sk-your-actual-key-here
```

## Run Your First Document

### Process a document:
```bash
python main.py your_document.pdf
```

That's it! The pipeline will:
1. ✅ Extract and summarize the document
2. ✅ Identify all persons and companies
3. ✅ Generate descriptions for each entity
4. ✅ Flag entities involved in money laundering or sanctions evasion

### Check the results:
```bash
# View the executive summary
cat outputs/summaries/your_document_summary.txt

# View extracted entities
cat outputs/entities/your_document_entities.txt

# View entity descriptions
cat outputs/entity_descriptions/your_document_entity_descriptions.txt

# View risk assessment
cat outputs/risk_flags/your_document_risk_assessment.txt
```

## Common Use Cases

### Process multiple documents at once:
```bash
python main.py doc1.pdf doc2.docx doc3.pdf
```

### Re-run just the risk analysis:
```bash
# First, process the document normally
python main.py contract.pdf

# Later, if you want to re-run just risk analysis
python main.py contract.pdf --stage-only 4
```

### Use custom API key:
```bash
python main.py document.pdf --api-key sk-different-key
```

## What Gets Created?

```
outputs/
├── extracted_text/              # Raw extracted text
├── summaries/                   # Executive + comprehensive summaries
├── entities/                    # Persons and companies found
├── entity_descriptions/         # Detailed entity profiles
└── risk_flags/                 # Risk assessment reports
```

Each output is available in both:
- **JSON format** - For programmatic access
- **TXT format** - For easy reading

## Need Help?

See the full documentation: `README_PIPELINE.md`

## Estimated Costs

Processing a typical 10-page document costs approximately **$0.15-0.30** in OpenAI API fees.

Breakdown:
- Summarization: ~$0.02-0.05
- Entity extraction: ~$0.01-0.03
- Entity descriptions: ~$0.05-0.10
- Risk analysis: ~$0.05-0.10
