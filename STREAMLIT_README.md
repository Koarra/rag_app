# Article Detective - Streamlit Application

## Overview

This application provides a complete document analysis pipeline with two interfaces:
1. **Streamlit Web UI** - User-friendly interface for uploading and processing documents
2. **Command Line** - Direct script execution for automation

## Features

- **6-Step Pipeline:**
  1. Extract text and generate summary
  2. Extract entities (persons & companies)
  3. Describe each entity
  4. Group similar entities (deduplication)
  5. Analyze risks (15 financial crime types)
  6. Extract relationships and create knowledge graph

- **Multiple File Support:** Process single or multiple documents
- **Progress Tracking:** Real-time progress updates
- **Interactive Results:** Tabbed interface for viewing outputs
- **Flexible Outputs:** All results saved to organized folders

## Installation

```bash
# Install required packages
pip install streamlit pandas llama-index llama-index-llms-azure-openai azure-identity pydantic python-docx PyPDF2 pdf2image pytesseract
```

## Usage

### Option 1: Streamlit Web App (Recommended)

```bash
# Run the Streamlit app
streamlit run streamlit_app.py
```

Then:
1. Upload one or more PDF/DOCX files
2. Click "Process Documents"
3. View results in tabs:
   - Summary
   - Entities
   - Risk Assessment
   - Knowledge Graph

**Output Structure:**
```
uploaded_documents/
├── document_name/          # Single file
│   └── outputs/
│       ├── summary.json
│       ├── entities.json
│       ├── entity_descriptions.json
│       ├── dict_unique_grouped_entity_summary.json
│       ├── risk_assessment.json
│       ├── entity_relationships.json
│       ├── entity_relationships_filtered.json
│       └── graph_elements.json
│
└── batch_abc123/           # Multiple files
    ├── file1.pdf
    ├── file2.pdf
    └── outputs/
        └── [same structure as above]
```

### Option 2: Command Line Pipeline

```bash
# Process a single document
python run_pipeline.py document.pdf

# Specify custom output folder
python run_pipeline.py document.pdf ./my_outputs

# Skip entity grouping step
python run_pipeline.py document.pdf ./outputs --skip-grouping
```

### Option 3: Individual Steps

Run each step manually with custom paths:

```bash
# Step 1: Extract and summarize
python step1_summarize.py document.pdf ./output_folder

# Step 2: Extract entities
python step2_extract_entities.py ./output_folder

# Step 3: Describe entities
python step3_describe_entities.py ./output_folder

# Step 4: Group entities
python step4_group_entities.py ./output_folder

# Step 5: Analyze risks
python step5_analyze_risks.py ./output_folder

# Step 6: Extract relationships
python step6_extract_relationships.py ./output_folder
```

## Output Files

| File | Description |
|------|-------------|
| `extracted_text.txt` | Raw text extracted from document |
| `summary.json` | Document summary |
| `entities.json` | List of persons and companies |
| `entity_descriptions.json` | Detailed descriptions for each entity |
| `dict_unique_grouped_entity_summary.json` | Deduplicated entities |
| `risk_assessment.json` | Entities flagged for financial crimes |
| `entity_relationships.json` | All entity relationships |
| `entity_relationships_filtered.json` | Meaningful relationships only |
| `graph_elements.json` | Knowledge graph (nodes & edges) |

## Financial Crimes Detected

The system checks for 15 types of financial crimes:
1. Money Laundering
2. Sanctions Evasion
3. Terrorist Financing
4. Bribery
5. Corruption
6. Embezzlement
7. Fraud
8. Tax Evasion
9. Insider Trading
10. Market Manipulation
11. Ponzi Scheme
12. Pyramid Scheme
13. Identity Theft
14. Cybercrime
15. Human Trafficking

## Authentication

All scripts use Azure OpenAI with `DefaultAzureCredential`. Ensure you have:
- Azure CLI logged in, OR
- Environment variables set (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET), OR
- Managed Identity configured

## Configuration

- **LLM Models:**
  - step1, step2, step3: `gpt-4o` and `gpt-4o-mini`
  - step4, step5, step6: `gpt-4o-mini`

- **Folder Structure:**
  - Single file: Uses filename as folder name
  - Multiple files: Creates hash-based folder (`batch_abc123`)

## Troubleshooting

**Issue:** OCR not working for scanned PDFs
```bash
# Install OCR dependencies
pip install pdf2image pytesseract
# Install tesseract (system-level)
# Ubuntu: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract
```

**Issue:** Azure authentication fails
```bash
# Login to Azure CLI
az login

# Or set environment variables
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

**Issue:** Streamlit app not finding scripts
- Ensure all step scripts are in the same directory as `streamlit_app.py`
- Run from the project root directory

## Tips

- **Large Documents:** For very large documents, processing may take several minutes
- **Multiple Files:** Batch processing creates a shared output folder
- **Knowledge Graph:** Use `graph_elements.json` with visualization tools like Cytoscape or D3.js
- **Custom Workflows:** Run individual steps for more control over the pipeline

## Examples

### Example 1: Quick Analysis
```bash
streamlit run streamlit_app.py
# Upload document.pdf through UI
# View results in browser
```

### Example 2: Batch Processing
```bash
python run_pipeline.py contract1.pdf ./batch1_output
python run_pipeline.py contract2.pdf ./batch2_output
python run_pipeline.py contract3.pdf ./batch3_output
```

### Example 3: Custom Pipeline
```bash
# Process with custom steps
python step1_summarize.py document.pdf ./output
python step2_extract_entities.py ./output
python step3_describe_entities.py ./output
# Skip grouping and go straight to risk analysis
python step5_analyze_risks.py ./output
python step6_extract_relationships.py ./output
```

## Support

For issues or questions:
1. Check the output logs in the Streamlit expanders
2. Verify Azure credentials are configured
3. Ensure all dependencies are installed
4. Check file permissions on output folders
