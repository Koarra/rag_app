"""
STEP 1: Extract text from document and generate summary

Usage: python step1_summarize.py <input_file.pdf>
Output: Creates summary.json with the document summary
"""

import sys
import json
from pathlib import Path
from openai import OpenAI
from docx import Document
import PyPDF2


def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    doc = Document(file_path)
    text_parts = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text)

    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells]
            text_parts.append(" | ".join(row_text))

    return "\n".join(text_parts)


def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text_parts = []

    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text and text.strip():
                text_parts.append(text)

    return "\n\n".join(text_parts)


def extract_text(file_path):
    """Extract text from PDF or DOCX"""
    extension = Path(file_path).suffix.lower()

    if extension == '.docx':
        return extract_text_from_docx(file_path)
    elif extension == '.pdf':
        return extract_text_from_pdf(file_path)
    else:
        print(f"Unsupported file type: {extension}")
        return None


def summarize_document(text, api_key):
    """Generate summary using OpenAI"""
    client = OpenAI(api_key=api_key)

    # Limit text to 15000 characters
    text_to_summarize = text[:15000]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
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

Document:
{text_to_summarize}"""
            }
        ],
        temperature=0.3,
        max_tokens=1000
    )

    return response.choices[0].message.content


def main():
    if len(sys.argv) < 2:
        print("Usage: python step1_summarize.py <input_file.pdf>")
        sys.exit(1)

    input_file = sys.argv[1]
    api_key = input("Enter your OpenAI API key: ") if len(sys.argv) < 3 else sys.argv[2]

    print(f"\n=== STEP 1: SUMMARIZE DOCUMENT ===")
    print(f"Processing: {input_file}")

    # Extract text
    print("Extracting text...")
    text = extract_text(input_file)

    if not text:
        print("Failed to extract text")
        sys.exit(1)

    print(f"Extracted {len(text)} characters")

    # Save extracted text
    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Saved: extracted_text.txt")

    # Generate summary
    print("Generating summary...")
    summary = summarize_document(text, api_key)

    # Save summary
    result = {
        "file_name": input_file,
        "summary": summary
    }

    with open("summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("Saved: summary.json")
    print(f"\nSummary:\n{summary}")
    print("\n=== STEP 1 COMPLETE ===\n")


if __name__ == "__main__":
    main()
