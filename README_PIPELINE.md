# Document Processing Pipeline

A comprehensive 4-stage pipeline for processing PDF and DOCX documents with entity extraction and risk analysis.

## Features

### Stage 1: Document Extraction & Summarization
- Extracts text from PDF and DOCX files
- OCR support for scanned documents
- Generates both executive and comprehensive summaries
- Handles large documents with intelligent chunking

### Stage 2: Entity Extraction
- Identifies persons and companies/organizations
- Uses OpenAI for accurate entity recognition
- Deduplicates and normalizes entity names
- Context-aware extraction

### Stage 3: Entity Description Generation
- Creates detailed descriptions for each entity
- Extracts roles, activities, and relationships
- Identifies financial details and transactions
- Batch processing for efficiency

### Stage 4: Risk Analysis
- Flags entities involved in:
  - Money laundering
  - Sanctions evasion
- Document-level and entity-level risk assessment
- Confidence scores and evidence extraction
- Comprehensive risk reports

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install system dependencies (for OCR):**

On Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

On macOS:
```bash
brew install tesseract poppler
```

On Windows:
- Download and install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Download and install Poppler: https://github.com/oschwartz10612/poppler-windows/releases

3. **Set up your OpenAI API key:**

Create a `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Or export as environment variable:
```bash
export OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Usage

### Basic Usage

Process a single document:
```bash
python main.py document.pdf
```

Process multiple documents:
```bash
python main.py doc1.pdf doc2.docx doc3.pdf
```

### Advanced Usage

**Provide API key via command line:**
```bash
python main.py document.pdf --api-key sk-your-key-here
```

**Skip certain stages (use previous results):**
```bash
# Skip stages 1 and 2, only run stages 3 and 4
python main.py document.pdf --skip-stages 1 2
```

**Run only a specific stage:**
```bash
# Run only stage 4 (risk analysis)
python main.py document.pdf --stage-only 4
```

### Run Individual Stages

You can also run each stage independently:

**Stage 1 - Document Processing:**
```bash
python src/document_processor.py document.pdf
```

**Stage 2 - Entity Extraction:**
```bash
python src/entity_extractor.py outputs/extracted_text/document_extracted.txt
```

**Stage 3 - Entity Analysis:**
```bash
python src/entity_analyzer.py outputs/entities/document_entities.json outputs/extracted_text/document_extracted.txt
```

**Stage 4 - Risk Analysis:**
```bash
python src/risk_analyzer.py outputs/extracted_text/document_extracted.txt outputs/entities/document_entities.json outputs/entity_descriptions/document_entity_descriptions.json
```

## Output Structure

All outputs are saved in the `outputs/` directory:

```
outputs/
├── extracted_text/           # Stage 1: Extracted document text
│   └── document_extracted.txt
├── summaries/                # Stage 1: Document summaries
│   ├── document_summary.json
│   └── document_summary.txt
├── entities/                 # Stage 2: Extracted entities
│   ├── document_entities.json
│   └── document_entities.txt
├── entity_descriptions/      # Stage 3: Entity descriptions
│   ├── document_entity_descriptions.json
│   └── document_entity_descriptions.txt
└── risk_flags/              # Stage 4: Risk assessments
    ├── document_risk_assessment.json
    └── document_risk_assessment.txt
```

### Output Formats

Each stage produces both:
- **JSON files** - Structured data for programmatic access
- **TXT files** - Human-readable formatted reports

## Configuration

Edit `src/utils/config.py` to customize:

- **OpenAI models** - Choose between different GPT models
- **Processing parameters** - Chunk sizes, thresholds, etc.
- **Directory structure** - Customize output locations
- **Retry settings** - API retry logic

## Cost Estimation

Approximate costs per document (10 pages):
- Stage 1 (Summarization): $0.02-0.05
- Stage 2 (Entity Extraction): $0.01-0.03
- Stage 3 (Entity Descriptions): $0.05-0.10
- Stage 4 (Risk Analysis): $0.05-0.10

**Total per document: ~$0.13-0.28**

Costs vary based on:
- Document length
- Number of entities
- Model selection (GPT-4 vs GPT-4o-mini)

## Examples

### Example 1: Process a contract
```bash
python main.py contracts/sales_agreement.pdf
```

Output includes:
- Summary of contract terms
- Entities: parties involved, companies
- Descriptions: roles and relationships
- Risk flags: any suspicious patterns

### Example 2: Batch process multiple documents
```bash
python main.py documents/*.pdf
```

### Example 3: Re-run risk analysis only
```bash
# First run all stages
python main.py document.pdf

# Later, re-run just risk analysis with updated logic
python main.py document.pdf --stage-only 4
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    main.py                               │
│              (Pipeline Orchestrator)                     │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Stage 1     │  │  Stage 2     │  │  Stage 3     │
│  Document    │─▶│  Entity      │─▶│  Entity      │
│  Processor   │  │  Extractor   │  │  Analyzer    │
└──────────────┘  └──────────────┘  └──────────────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │  Stage 4     │
                                    │  Risk        │
                                    │  Analyzer    │
                                    └──────────────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │ Outputs      │
                                    │ (JSON + TXT) │
                                    └──────────────┘
```

## Troubleshooting

**OCR not working:**
- Ensure Tesseract is installed: `tesseract --version`
- Ensure Poppler is installed: `pdftoppm -v`

**API errors:**
- Check your API key is valid
- Verify you have sufficient OpenAI credits
- Check rate limits

**Missing dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

**File not found errors:**
- Use absolute paths or ensure you're in the correct directory
- Check file permissions

## Security Notes

- **API Keys**: Never commit `.env` files to git
- **Sensitive Documents**: Ensure compliance with data handling policies
- **Output Files**: Review and secure output files containing extracted information

## License

This project is for defensive security and compliance analysis purposes only.
