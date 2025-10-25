# Simple Document Risk Analyzer - Streamlit App

A simple, single-file Streamlit application for analyzing documents for entities and financial crime risks.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Your OpenAI API Key
```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

Or create a `.env` file:
```bash
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

### 3. Run the App
```bash
streamlit run app_simple.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

1. **Open the app** in your browser
2. **Upload one or more documents** (PDF or DOCX)
3. **Click "Process Documents"**
4. **View the results** in 4 stages:
   - 📝 Document Summary
   - 👥 Extracted Entities (Persons & Companies)
   - 📋 Entity Descriptions
   - ⚠️ Risk Assessment (Money Laundering & Sanctions Evasion)
5. **Download results** as JSON

## Features

### Stage 1: Document Summary
- Extracts text from uploaded documents
- Generates comprehensive summary using OpenAI
- Shows key information: purpose, parties, dates, amounts, decisions

### Stage 2: Entity Extraction
- Identifies all persons mentioned in the document
- Identifies all companies/organizations
- Uses structured outputs for reliable extraction

### Stage 3: Entity Descriptions
- Creates detailed profile for each entity
- Extracts: role, description, activities, related entities, financial details
- Context-aware analysis based on document content

### Stage 4: Risk Assessment
- **Document-level risk:** Overall assessment with risk levels
- **Entity-level risk:** Flags specific entities for:
  - Money Laundering
  - Sanctions Evasion
- Provides evidence, reasoning, and confidence scores
- Shows red flags and suspicious patterns

## UI Features

- **Multi-file upload:** Process multiple documents at once
- **Expandable sections:** Each stage has its own section
- **Visual risk indicators:** Color-coded risk levels (🔴 High, 🟡 Medium, 🟢 Low)
- **Download results:** Export all results as JSON
- **Real-time progress:** See processing status for each stage

## Example Output

After processing a document, you'll see:

```
📄 Processing: contract.pdf
✓ Extracted 15,432 characters

📝 Stage 1: Document Summary
[Summary text...]

👥 Stage 2: Extracted Entities
Persons:
- John Smith
- Jane Doe

Companies:
- ABC Corporation
- XYZ Limited

📋 Stage 3: Entity Descriptions
[Detailed entity profiles...]

⚠️ Stage 4: Risk Assessment
Overall Risk: 🟡 MEDIUM
Money Laundering: 🟡 MEDIUM
Sanctions Evasion: 🟢 LOW

Flagged Entities: 1
[Detailed risk analysis...]
```

## Cost Estimation

Processing a typical 10-page document costs approximately **$0.15-0.30** in OpenAI API fees.

## Troubleshooting

**"Please set OPENAI_API_KEY environment variable"**
- Set your API key before running the app
- `export OPENAI_API_KEY=sk-your-key-here`

**Upload not working**
- Only PDF and DOCX files are supported
- Check file is not corrupted

**Processing fails**
- Check your OpenAI API key is valid
- Verify you have sufficient API credits
- Check network connection

## File Structure

```
app_simple.py          # Single-file Streamlit application (all code here)
requirements.txt       # Python dependencies
.env.example          # API key template
```

## Comparison: Simple vs Modular

**This app (app_simple.py):**
- ✅ Single file - all code in one place
- ✅ Simple to understand and modify
- ✅ Streamlit UI
- ✅ Upload and process in browser
- ✅ Visual results

**Modular version (main.py):**
- Factorized code across multiple modules
- Command-line interface
- Better for batch processing
- More configurable

Use whichever fits your needs better!

## Security Notes

- Never commit API keys to git
- Be careful with sensitive documents
- Review output before sharing

## Support

For issues or questions, check:
- OpenAI API documentation: https://platform.openai.com/docs
- Streamlit documentation: https://docs.streamlit.io
