"""
Streamlit Application for Article Detective - Document Analysis Pipeline

This app processes documents through a 6-step pipeline:
1. Extract text and summarize
2. Extract entities (persons & companies)
3. Describe each entity
4. Group similar entities
5. Analyze risks (financial crimes)
6. Extract relationships and create knowledge graph
"""

import streamlit as st
import subprocess
import json
from pathlib import Path
import hashlib
import re
from datetime import datetime
import pandas as pd

# Configuration
ASSET_FOLDER = Path("./uploaded_documents")
ASSET_FOLDER.mkdir(parents=True, exist_ok=True)


def transform_string(input_string):
    """Transform string for use as filename or folder name."""
    cleaned = re.sub(r'[^\w\s-]', '', input_string)
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned.lower()


def run_step(script_name, args, step_name):
    """Run a step script and show progress"""
    try:
        cmd = ["python", script_name] + args
        st.info(f"Running {step_name}...")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        st.success(f"✓ {step_name} completed")
        with st.expander(f"View {step_name} output"):
            st.code(result.stdout)

        return True
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Error in {step_name}")
        st.code(e.stderr)
        return False


def main():
    st.set_page_config(
        page_title="Article Detective",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🔍 Article Detective - Document Analysis")
    st.markdown("---")

    # File upload section
    st.header("1. Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose your files",
        type=["docx", "pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDF or DOCX files for analysis"
    )

    if uploaded_files:
        st.success(f"✓ {len(uploaded_files)} file(s) uploaded")

        # Create folder structure
        if len(uploaded_files) == 1:
            # Single file: use filename as folder
            name_article, file_ext = Path(uploaded_files[0].name).stem, Path(uploaded_files[0].name).suffix
            folder_name = transform_string(name_article)
        else:
            # Multiple files: create hash-based folder
            filenames = sorted([transform_string(Path(f.name).stem) for f in uploaded_files])
            unique_string = "_".join(filenames)
            folder_hash = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()[:16]
            folder_name = f"batch_{folder_hash}"

        # Create output folder
        output_folder = ASSET_FOLDER / folder_name
        output_folder.mkdir(parents=True, exist_ok=True)

        # Save uploaded files
        st.write(f"**Output folder:** `{output_folder}`")

        file_paths = []
        for uploaded_file in uploaded_files:
            name_article, file_ext = Path(uploaded_file.name).stem, Path(uploaded_file.name).suffix
            article_cleaned = transform_string(name_article)
            file_path = output_folder / f"{article_cleaned}{file_ext}"

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)
            st.write(f"- Saved: `{file_path.name}`")

        st.markdown("---")

        # Process documents button
        if st.button("🚀 Process Documents", type="primary"):
            st.header("2. Processing Pipeline")

            progress_bar = st.progress(0)
            status_text = st.empty()

            all_success = True

            for i, file_path in enumerate(file_paths):
                st.subheader(f"Processing: {file_path.name}")
                file_output_folder = output_folder / file_path.stem
                file_output_folder.mkdir(parents=True, exist_ok=True)

                # Step 1: Summarize
                status_text.text(f"Step 1/6: Extracting text and summarizing...")
                if not run_step("step1_summarize.py", [str(file_path), str(file_output_folder)], "Step 1: Summarize"):
                    all_success = False
                    break
                progress_bar.progress((i * 6 + 1) / (len(file_paths) * 6))

                # Step 2: Extract entities
                status_text.text(f"Step 2/6: Extracting entities...")
                if not run_step("step2_extract_entities.py", [str(file_output_folder)], "Step 2: Extract Entities"):
                    all_success = False
                    break
                progress_bar.progress((i * 6 + 2) / (len(file_paths) * 6))

                # Step 3: Describe entities
                status_text.text(f"Step 3/6: Describing entities...")
                if not run_step("step3_describe_entities.py", [str(file_output_folder)], "Step 3: Describe Entities"):
                    all_success = False
                    break
                progress_bar.progress((i * 6 + 3) / (len(file_paths) * 6))

                # Step 4: Group entities
                status_text.text(f"Step 4/6: Grouping similar entities...")
                if not run_step("step4_group_entities.py", [str(file_output_folder)], "Step 4: Group Entities"):
                    all_success = False
                    break
                progress_bar.progress((i * 6 + 4) / (len(file_paths) * 6))

                # Step 5: Analyze risks
                status_text.text(f"Step 5/6: Analyzing risks...")
                if not run_step("step5_analyze_risks.py", [str(file_output_folder)], "Step 5: Analyze Risks"):
                    all_success = False
                    break
                progress_bar.progress((i * 6 + 5) / (len(file_paths) * 6))

                # Step 6: Extract relationships
                status_text.text(f"Step 6/6: Extracting relationships...")
                if not run_step("step6_extract_relationships.py", [str(file_output_folder)], "Step 6: Extract Relationships"):
                    all_success = False
                    break
                progress_bar.progress((i * 6 + 6) / (len(file_paths) * 6))

            if all_success:
                status_text.text("✅ All steps completed successfully!")
                progress_bar.progress(1.0)
                st.balloons()

                st.markdown("---")
                st.header("3. Results")

                # Display results for each file
                for file_path in file_paths:
                    file_output_folder = output_folder / file_path.stem
                    st.subheader(f"📄 Results for: {file_path.name}")

                    tabs = st.tabs(["Summary", "Entities", "Risk Assessment", "Knowledge Graph"])

                    # Tab 1: Summary
                    with tabs[0]:
                        try:
                            with open(file_output_folder / "summary.json", "r") as f:
                                summary = json.load(f)
                            st.write(summary["summary"])
                        except Exception as e:
                            st.error(f"Could not load summary: {e}")

                    # Tab 2: Entities
                    with tabs[1]:
                        try:
                            with open(file_output_folder / "dict_unique_grouped_entity_summary.json", "r") as f:
                                entities = json.load(f)

                            df = pd.DataFrame([
                                {"Entity": name, "Description": desc[:200] + "..." if len(desc) > 200 else desc}
                                for name, desc in entities.items()
                            ])
                            st.dataframe(df, use_container_width=True)
                        except Exception as e:
                            st.error(f"Could not load entities: {e}")

                    # Tab 3: Risk Assessment
                    with tabs[2]:
                        try:
                            with open(file_output_folder / "risk_assessment.json", "r") as f:
                                risks = json.load(f)

                            flagged = risks.get("flagged_entities", [])
                            if flagged:
                                st.warning(f"⚠️ {len(flagged)} flagged entities found")
                                for entity in flagged:
                                    with st.expander(f"🚩 {entity['entity_name']} - {entity['risk_level'].upper()} risk"):
                                        st.write(f"**Crimes:** {', '.join(entity['crimes_flagged'])}")
                                        st.write(f"**Confidence:** {entity['confidence']}")
                                        st.write(f"**Evidence:**")
                                        for evidence in entity['evidence']:
                                            st.write(f"- {evidence}")
                                        st.write(f"**Reasoning:** {entity['reasoning']}")
                            else:
                                st.success("✅ No flagged entities")
                        except Exception as e:
                            st.error(f"Could not load risk assessment: {e}")

                    # Tab 4: Knowledge Graph
                    with tabs[3]:
                        try:
                            with open(file_output_folder / "entity_relationships_filtered.json", "r") as f:
                                relationships = json.load(f)

                            st.write(f"**Total relationships:** {len(relationships)}")

                            df_rel = pd.DataFrame([
                                {
                                    "Entity 1": r["entities"][0],
                                    "Relationship": r["relationship"],
                                    "Entity 2": r["entities"][1],
                                    "Involves Flagged": "🚩" if r["involves_flagged"] else ""
                                }
                                for r in relationships
                            ])
                            st.dataframe(df_rel, use_container_width=True)

                            st.info("💡 Tip: graph_elements.json can be used with visualization tools like Cytoscape or D3.js")
                        except Exception as e:
                            st.error(f"Could not load relationships: {e}")

            else:
                st.error("❌ Processing failed. Please check the errors above.")


if __name__ == "__main__":
    main()
