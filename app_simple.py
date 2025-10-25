"""
Simple Document Processing Application
Upload PDF/DOCX documents and process through 4 stages:
1. Extract text and summarize
2. Extract entities (persons & companies)
3. Generate entity descriptions
4. Flag entities for money laundering and sanctions evasion
"""

import streamlit as st
import os
import json
import tempfile
from pathlib import Path
from openai import OpenAI
from docx import Document
import PyPDF2

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        st.error("Please set OPENAI_API_KEY environment variable")
        st.stop()
    return OpenAI(api_key=api_key)

# Extract text from DOCX
def extract_docx(file_path):
    doc = Document(file_path)
    text_content = []

    for para in doc.paragraphs:
        if para.text.strip():
            text_content.append(para.text)

    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells]
            text_content.append(" | ".join(row_text))

    return "\n".join(text_content)

# Extract text from PDF
def extract_pdf(file_path):
    text_content = []

    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                text_content.append(text)

    return "\n\n".join(text_content)

# Extract text from file
def extract_text(file_path):
    ext = Path(file_path).suffix.lower()

    if ext == '.docx':
        return extract_docx(file_path)
    elif ext == '.pdf':
        return extract_pdf(file_path)
    else:
        return f"Unsupported file format: {ext}"

# Stage 1: Summarize document
def summarize_document(client, text):
    st.write("🔄 Generating summary...")

    messages = [
        {
            "role": "system",
            "content": "You are an expert document analyst. Summarize documents clearly and accurately."
        },
        {
            "role": "user",
            "content": f"""Provide a comprehensive summary of this document.
Include:
- Main purpose and context
- Key parties involved
- Important dates and amounts
- Critical actions or decisions
- Relevant details

Document:
{text[:15000]}"""  # Limit to ~15k chars
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=1000
    )

    return response.choices[0].message.content

# Stage 2: Extract entities
def extract_entities(client, text):
    st.write("🔄 Extracting entities (persons & companies)...")

    messages = [
        {
            "role": "system",
            "content": """You are an expert entity extraction system. Extract all persons and companies/organizations mentioned in the document.

Guidelines:
- Persons: Extract full names of individuals (e.g., "John Smith", "Dr. Jane Doe")
- Companies: Extract company names, organizations, institutions (e.g., "ABC Corporation", "Ministry of Finance")
- Be thorough - extract all entities mentioned"""
        },
        {
            "role": "user",
            "content": f"Extract all persons and companies from this document:\n\n{text[:15000]}"
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.1,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "entity_extraction",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "persons": {
                            "type": "array",
                            "description": "List of person names",
                            "items": {"type": "string"}
                        },
                        "companies": {
                            "type": "array",
                            "description": "List of company names",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["persons", "companies"],
                    "additionalProperties": False
                }
            }
        }
    )

    return json.loads(response.choices[0].message.content)

# Stage 3: Describe entities
def describe_entities(client, text, entities):
    st.write("🔄 Generating entity descriptions...")

    all_entity_names = entities.get('persons', []) + entities.get('companies', [])

    if not all_entity_names:
        return {}

    # Process in one batch (limit to first 10 for simplicity)
    entity_names = all_entity_names[:10]

    messages = [
        {
            "role": "system",
            "content": """You are an expert analyst. For each entity, provide:
1. A description based on the document
2. Their role or position
3. Key activities they're involved in
4. Related entities
5. Any financial details

Be factual and precise."""
        },
        {
            "role": "user",
            "content": f"""Analyze these entities: {', '.join(entity_names)}

Document:
{text[:12000]}

Provide detailed analysis for each entity."""
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=2000,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "entity_descriptions",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "description": {"type": "string"},
                                    "role": {"type": "string"},
                                    "key_activities": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "related_entities": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "financial_details": {"type": "string"}
                                },
                                "required": ["name", "type", "description", "role", "key_activities", "related_entities", "financial_details"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["entities"],
                    "additionalProperties": False
                }
            }
        }
    )

    result = json.loads(response.choices[0].message.content)

    # Convert to dict
    descriptions = {}
    for entity in result.get('entities', []):
        descriptions[entity['name']] = entity

    return descriptions

# Stage 4: Risk analysis
def analyze_risks(client, text, entities, entity_descriptions):
    st.write("🔄 Analyzing risks (money laundering & sanctions evasion)...")

    # Document-level risk
    messages = [
        {
            "role": "system",
            "content": """You are an expert financial crime analyst specializing in anti-money laundering (AML) and sanctions compliance.

Analyze documents for indicators of:

MONEY LAUNDERING:
  • Unusual transaction patterns
  • Shell companies or front companies
  • Layering activities
  • Structuring/Smurfing
  • High-risk jurisdictions
  • Rapid movement of funds

SANCTIONS EVASION:
  • Transactions with sanctioned countries
  • Use of front companies
  • Re-routing through third countries
  • False documentation
  • Sanctioned individuals/entities
  • Prohibited goods

Provide objective, evidence-based analysis."""
        },
        {
            "role": "user",
            "content": f"""Analyze this document for money laundering and sanctions evasion indicators.

Document:
{text[:15000]}

Provide a comprehensive risk assessment."""
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.1,
        max_tokens=1500,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "document_risk_assessment",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "overall_risk_level": {
                            "type": "string",
                            "enum": ["high", "medium", "low", "none"]
                        },
                        "money_laundering_risk": {
                            "type": "string",
                            "enum": ["high", "medium", "low", "none"]
                        },
                        "sanctions_evasion_risk": {
                            "type": "string",
                            "enum": ["high", "medium", "low", "none"]
                        },
                        "red_flags": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "suspicious_patterns": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "analysis_summary": {"type": "string"}
                    },
                    "required": ["overall_risk_level", "money_laundering_risk", "sanctions_evasion_risk", "red_flags", "suspicious_patterns", "analysis_summary"],
                    "additionalProperties": False
                }
            }
        }
    )

    document_risk = json.loads(response.choices[0].message.content)

    # Entity-level risk
    all_entity_names = entities.get('persons', []) + entities.get('companies', [])
    entity_contexts = []

    for name in all_entity_names[:10]:  # Limit to 10
        desc = entity_descriptions.get(name, {})
        context = f"""
Entity: {name}
Type: {desc.get('type', 'unknown')}
Role: {desc.get('role', 'unknown')}
Description: {desc.get('description', 'No description')}
Activities: {', '.join(desc.get('key_activities', []))}
"""
        entity_contexts.append(context)

    if entity_contexts:
        messages = [
            {
                "role": "system",
                "content": """You are an expert in financial crime detection. Analyze entities for involvement in:
1. Money Laundering
2. Sanctions Evasion

Only flag entities with credible evidence. Provide confidence scores."""
            },
            {
                "role": "user",
                "content": f"""Analyze these entities for money laundering and sanctions evasion:

{chr(10).join(entity_contexts)}

Flag only entities with credible evidence."""
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.1,
            max_tokens=2000,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "entity_risk_assessment",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "flagged_entities": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "entity_name": {"type": "string"},
                                        "entity_type": {"type": "string"},
                                        "crimes_flagged": {
                                            "type": "array",
                                            "items": {
                                                "type": "string",
                                                "enum": ["money_laundering", "sanctions_evasion"]
                                            }
                                        },
                                        "risk_level": {
                                            "type": "string",
                                            "enum": ["high", "medium", "low"]
                                        },
                                        "confidence": {"type": "number"},
                                        "evidence": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "reasoning": {"type": "string"}
                                    },
                                    "required": ["entity_name", "entity_type", "crimes_flagged", "risk_level", "confidence", "evidence", "reasoning"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["flagged_entities"],
                        "additionalProperties": False
                    }
                }
            }
        )

        entity_risks = json.loads(response.choices[0].message.content)
    else:
        entity_risks = {"flagged_entities": []}

    return {
        "document_risk": document_risk,
        "entity_risks": entity_risks
    }

# Process a single document
def process_document(client, file_path, file_name):
    st.subheader(f"📄 Processing: {file_name}")

    # Extract text
    with st.spinner("Extracting text..."):
        text = extract_text(file_path)
        if text.startswith("Error") or text.startswith("Unsupported"):
            st.error(text)
            return None
        st.success(f"✓ Extracted {len(text)} characters")

    results = {
        "file_name": file_name,
        "text": text
    }

    # Stage 1: Summarize
    with st.expander("📝 Stage 1: Document Summary", expanded=True):
        summary = summarize_document(client, text)
        results["summary"] = summary
        st.write(summary)

    # Stage 2: Extract entities
    with st.expander("👥 Stage 2: Extracted Entities", expanded=True):
        entities = extract_entities(client, text)
        results["entities"] = entities

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Persons:**")
            for person in entities.get('persons', []):
                st.write(f"- {person}")
        with col2:
            st.write("**Companies:**")
            for company in entities.get('companies', []):
                st.write(f"- {company}")

    # Stage 3: Describe entities
    with st.expander("📋 Stage 3: Entity Descriptions", expanded=True):
        descriptions = describe_entities(client, text, entities)
        results["descriptions"] = descriptions

        for entity_name, desc in descriptions.items():
            st.write(f"**{entity_name}** ({desc['type']})")
            st.write(f"*Role:* {desc['role']}")
            st.write(f"*Description:* {desc['description']}")
            if desc['key_activities']:
                st.write(f"*Activities:* {', '.join(desc['key_activities'])}")
            if desc['financial_details']:
                st.write(f"*Financial:* {desc['financial_details']}")
            st.write("---")

    # Stage 4: Risk analysis
    with st.expander("⚠️ Stage 4: Risk Assessment", expanded=True):
        risks = analyze_risks(client, text, entities, descriptions)
        results["risks"] = risks

        doc_risk = risks["document_risk"]

        # Document risk
        st.write("**Document-Level Risk:**")

        col1, col2, col3 = st.columns(3)
        with col1:
            risk_color = {"high": "🔴", "medium": "🟡", "low": "🟢", "none": "⚪"}
            st.metric("Overall Risk",
                     f"{risk_color.get(doc_risk['overall_risk_level'], '⚪')} {doc_risk['overall_risk_level'].upper()}")
        with col2:
            st.metric("Money Laundering",
                     f"{risk_color.get(doc_risk['money_laundering_risk'], '⚪')} {doc_risk['money_laundering_risk'].upper()}")
        with col3:
            st.metric("Sanctions Evasion",
                     f"{risk_color.get(doc_risk['sanctions_evasion_risk'], '⚪')} {doc_risk['sanctions_evasion_risk'].upper()}")

        st.write(f"**Analysis:** {doc_risk['analysis_summary']}")

        if doc_risk['red_flags']:
            st.write("**Red Flags:**")
            for flag in doc_risk['red_flags']:
                st.write(f"- {flag}")

        if doc_risk['suspicious_patterns']:
            st.write("**Suspicious Patterns:**")
            for pattern in doc_risk['suspicious_patterns']:
                st.write(f"- {pattern}")

        # Entity risks
        flagged = risks["entity_risks"]["flagged_entities"]
        if flagged:
            st.write("---")
            st.write(f"**Flagged Entities: {len(flagged)}**")

            for entity in flagged:
                st.write(f"### {entity['entity_name']} ({entity['entity_type']})")
                st.write(f"**Risk Level:** {entity['risk_level'].upper()} (Confidence: {entity['confidence']:.2f})")
                st.write(f"**Crimes:** {', '.join(entity['crimes_flagged']).replace('_', ' ').title()}")
                st.write(f"**Reasoning:** {entity['reasoning']}")
                st.write("**Evidence:**")
                for evidence in entity['evidence']:
                    st.write(f"- {evidence}")
                st.write("---")
        else:
            st.success("✓ No entities flagged for criminal activity")

    # Download results
    st.download_button(
        label="📥 Download Results (JSON)",
        data=json.dumps(results, indent=2),
        file_name=f"{Path(file_name).stem}_results.json",
        mime="application/json"
    )

    return results

# Main app
def main():
    st.set_page_config(
        page_title="Document Risk Analyzer",
        page_icon="📄",
        layout="wide"
    )

    st.title("📄 Document Risk Analyzer")
    st.write("Upload PDF or DOCX documents to analyze for entities and financial crime risks")

    # Sidebar
    with st.sidebar:
        st.header("About")
        st.write("""
        This tool processes documents through 4 stages:

        1. **Extract & Summarize** - Generate document summary
        2. **Extract Entities** - Identify persons & companies
        3. **Describe Entities** - Generate detailed profiles
        4. **Risk Analysis** - Flag money laundering & sanctions evasion
        """)

        st.write("---")
        st.write("**Requirements:**")
        st.write("- Set OPENAI_API_KEY environment variable")
        st.write("- Upload PDF or DOCX files")

    # File upload
    uploaded_files = st.file_uploader(
        "Upload Documents (PDF or DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        client = get_openai_client()

        st.write(f"**{len(uploaded_files)} file(s) uploaded**")

        if st.button("🚀 Process Documents", type="primary"):
            all_results = []

            for uploaded_file in uploaded_files:
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                try:
                    result = process_document(client, tmp_path, uploaded_file.name)
                    if result:
                        all_results.append(result)
                finally:
                    # Clean up temp file
                    os.unlink(tmp_path)

                st.write("---")

            st.success(f"✅ Processed {len(all_results)} document(s) successfully!")

            # Download all results
            if len(all_results) > 1:
                st.download_button(
                    label="📥 Download All Results (JSON)",
                    data=json.dumps(all_results, indent=2),
                    file_name="all_results.json",
                    mime="application/json"
                )

if __name__ == "__main__":
    main()
