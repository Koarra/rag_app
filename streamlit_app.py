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
import os
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle

# Configuration - Support both Domino and local environments
if "DOMINO_DATASETS_DIR" in os.environ and "DOMINO_PROJECT_NAME" in os.environ:
    # Running on Domino Data Lab
    ASSET_FOLDER = (
        Path(os.environ["DOMINO_DATASETS_DIR"])
        / "local"
        / os.environ["DOMINO_PROJECT_NAME"]
        / "articledetectivereview_assets"
        / "uploaded_documents"
    )
else:
    # Running locally
    ASSET_FOLDER = Path("./uploaded_documents")

ASSET_FOLDER.mkdir(parents=True, exist_ok=True)


def transform_string(input_string):
    """Transform string for use as filename or folder name."""
    cleaned = re.sub(r'[^\w\s-]', '', input_string)
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned.lower()


def run_step(script_name, args):
    """Run a step script silently"""
    try:
        cmd = ["python", script_name] + args

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def main():
    st.set_page_config(
        page_title="Article Detective",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🔍 Article Detective - Document Analysis")

    # Show environment info
    if "DOMINO_DATASETS_DIR" in os.environ:
        st.info(f"🏢 Running on Domino Data Lab - Output folder: `{ASSET_FOLDER}`")
    else:
        st.info(f"💻 Running locally - Output folder: `{ASSET_FOLDER}`")

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
            # Track processing time
            import time
            start_time = time.time()

            processing_placeholder = st.empty()
            processing_placeholder.info("⏳ Processing documents...")

            all_success = True
            errors = []

            # Create outputs subfolder
            outputs_folder = output_folder / "outputs"
            outputs_folder.mkdir(parents=True, exist_ok=True)

            # Process all files through step 1
            for file_path in file_paths:
                success, stdout, stderr = run_step("step1_summarize.py", [str(file_path), str(outputs_folder)])
                if not success:
                    all_success = False
                    errors.append(f"Step 1 failed for {file_path.name}: {stderr}")
                    break

            # Run remaining steps once (they process all entities together)
            if all_success:
                steps = [
                    ("step2_extract_entities.py", [str(outputs_folder)]),
                    ("step3_describe_entities.py", [str(outputs_folder)]),
                    ("step4_group_entities.py", [str(outputs_folder)]),
                    ("step5_analyze_risks.py", [str(outputs_folder)]),
                    ("step6_extract_relationships.py", [str(outputs_folder)])
                ]

                for script, args in steps:
                    success, stdout, stderr = run_step(script, args)
                    if not success:
                        all_success = False
                        errors.append(f"{script} failed: {stderr}")
                        break

            # Calculate processing time
            end_time = time.time()
            processing_time = end_time - start_time

            # Clear processing message
            processing_placeholder.empty()

            if all_success:
                st.success(f"✅ Processing completed successfully in {processing_time:.2f} seconds")
                st.balloons()

                st.markdown("---")
                st.header("3. Results")

                # Display results from the outputs folder
                st.subheader(f"📄 Analysis Results")

                # ============================================
                # Section 1: Article Summary
                # ============================================
                st.markdown("---")
                with st.container():
                    st.markdown("### 📄 Article Summary")

                    try:
                        # Check for combined summary first
                        combined_summary_path = outputs_folder / "combined_summary.json"
                        if combined_summary_path.exists():
                            with open(combined_summary_path, "r") as f:
                                combined = json.load(f)

                            if 'edit_mode_summary' not in st.session_state:
                                st.session_state.edit_mode_summary = False
                            if 'summary_text' not in st.session_state:
                                st.session_state.summary_text = combined["combined_summary"]

                            def toggle_edit_summary():
                                st.session_state.edit_mode_summary = not st.session_state.edit_mode_summary

                            def apply_changes_summary():
                                st.session_state.summary_text = st.session_state.temp_summary_text
                                st.session_state.edit_mode_summary = False
                                st.toast("Feedback successfully submitted!")

                            if not st.session_state.edit_mode_summary:
                                st.write(st.session_state.summary_text)
                                st.caption(f"Based on {combined['file_count']} document(s): {', '.join(combined['files'])}")
                                st.button("Edit Summary", on_click=toggle_edit_summary, key="edit_btn_summary")
                            else:
                                st.text_area("Please edit your text:", value=st.session_state.summary_text, key="temp_summary_text", height=200)
                                st.button("Apply and share feedback", on_click=apply_changes_summary, key="apply_btn_summary")

                        # Show individual summaries in expanders
                        summary_files = sorted(outputs_folder.glob("summary_*.json"))
                        if summary_files and len(summary_files) > 1:
                            st.markdown("**Individual Summaries:**")
                            for summary_file in summary_files:
                                with open(summary_file, "r") as f:
                                    summary = json.load(f)
                                with st.expander(f"📄 {Path(summary['file_name']).name}"):
                                    st.write(summary["summary"])
                        elif summary_files and len(summary_files) == 1:
                            # Single file case
                            with open(summary_files[0], "r") as f:
                                summary = json.load(f)

                            if 'edit_mode_summary' not in st.session_state:
                                st.session_state.edit_mode_summary = False
                            if 'summary_text' not in st.session_state:
                                st.session_state.summary_text = summary["summary"]

                            def toggle_edit_summary():
                                st.session_state.edit_mode_summary = not st.session_state.edit_mode_summary

                            def apply_changes_summary():
                                st.session_state.summary_text = st.session_state.temp_summary_text
                                st.session_state.edit_mode_summary = False
                                st.toast("Feedback successfully submitted!")

                            if not st.session_state.edit_mode_summary:
                                st.write(st.session_state.summary_text)
                                st.button("Edit Summary", on_click=toggle_edit_summary, key="edit_btn_summary")
                            else:
                                st.text_area("Please edit your text:", value=st.session_state.summary_text, key="temp_summary_text", height=200)
                                st.button("Apply and share feedback", on_click=apply_changes_summary, key="apply_btn_summary")
                    except Exception as e:
                        st.error(f"Could not load summary: {e}")

                # ============================================
                # Section 2: Entity Summaries
                # ============================================
                st.markdown("---")
                with st.container():
                    st.markdown("### 👥 Entity Summaries")

                    try:
                        with open(outputs_folder / "dict_unique_grouped_entity_summary.json", "r") as f:
                            entities = json.load(f)

                        # Entity selector
                        entity_list = list(entities.keys())
                        if entity_list:
                            selected_entity = st.selectbox("**Select an entity**", entity_list)

                            if selected_entity:
                                st.info("Entity Summary:")
                                st.write(entities[selected_entity])

                        # Also show as expandable table
                        with st.expander("View All Entities"):
                            df = pd.DataFrame([
                                {"Entity": name, "Description": desc[:200] + "..." if len(desc) > 200 else desc}
                                for name, desc in entities.items()
                            ])
                            st.dataframe(df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not load entities: {e}")

                # ============================================
                # Section 3: Risk Assessment
                # ============================================
                st.markdown("---")
                with st.container():
                    st.markdown("### ⚠️ Risk Assessment")

                    try:
                        with open(outputs_folder / "risk_assessment.json", "r") as f:
                            risks = json.load(f)

                        flagged = risks.get("flagged_entities", [])
                        if flagged:
                            st.warning(f"⚠️ {len(flagged)} flagged entities found")
                            for entity in flagged:
                                with st.expander(f"🚩 {entity['entity_name']} - {entity['risk_level'].upper()} risk"):
                                    st.write(f"**Type:** {entity['entity_type']}")
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

                # ============================================
                # Section 4: Entity Relationships (Graph)
                # ============================================
                st.markdown("---")
                with st.container():
                    st.markdown("### 🔗 Entity Relationships")

                    try:
                        # Load graph elements for visualization
                        with open(outputs_folder / "graph_elements.json", "r") as f:
                            elements = json.load(f)

                        # Style nodes & edges for graph
                        edge_styles = [
                            EdgeStyle("Owner", caption="label", directed=False),
                            EdgeStyle("Investor", caption="label", directed=False),
                            EdgeStyle("Partner", caption="label", directed=False),
                            EdgeStyle("Shareholder", caption="label", directed=False),
                            EdgeStyle("Representative", caption="label", directed=False),
                            EdgeStyle("Beneficiary", caption="label", directed=False),
                            EdgeStyle("Other relationship", caption="label", directed=False),
                        ]

                        node_styles = [
                            NodeStyle("PERSON", "#FF7F3E", "name", "person"),
                            NodeStyle("FLAGGED", "#2A629A", "name", "flag"),
                        ]

                        st_link_analysis(
                            elements,
                            node_styles=node_styles,
                            edge_styles=edge_styles,
                            layout="cose",
                            key="knowledge_graph"
                        )

                    except Exception as e:
                        st.error(f"Could not load knowledge graph: {e}")

                # ============================================
                # Section 5: Relationship Details
                # ============================================
                st.markdown("---")
                with st.container():
                    st.markdown("### 📊 Relationship Details")

                    try:
                        with open(outputs_folder / "entity_relationships_filtered.json", "r") as f:
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
                        st.dataframe(df_rel, use_container_width=True, height=400)

                    except Exception as e:
                        st.error(f"Could not load relationships: {e}")

            else:
                st.error(f"❌ Processing failed after {processing_time:.2f} seconds")
                if errors:
                    st.subheader("Error Details")
                    for error in errors:
                        st.code(error)


if __name__ == "__main__":
    main()
