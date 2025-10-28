"""
Article Detective - Complete Streamlit Application
Integrates document processing pipeline with original UI features
"""

import streamlit as st
from pathlib import Path
import os
import hashlib
import subprocess
import json
import glob
import pandas as pd
import re
from datetime import datetime

# Import optional components (graceful degradation if not available)
try:
    from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
    HAS_LINK_ANALYSIS = True
except ImportError:
    HAS_LINK_ANALYSIS = False
    st.warning("st_link_analysis not installed. Knowledge graph visualization will be limited.")

# Configuration
if "DOMINO_DATASETS_DIR" in os.environ and "DOMINO_PROJECT_NAME" in os.environ:
    ASSET_FOLDER = (
        Path(os.environ["DOMINO_DATASETS_DIR"])
        / "local"
        / os.environ["DOMINO_PROJECT_NAME"]
        / "articledetectivereview_assets"
    )
else:
    ASSET_FOLDER = Path("./articledetectivereview_assets")

ASSET_FOLDER.mkdir(parents=True, exist_ok=True)

__version__ = "2.0.0"


def transform_string(input_string):
    """Transform string for use as filename or folder name."""
    cleaned = re.sub(r'[^\w\s-]', '', input_string)
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned.lower()


def run_pipeline_step(script_name, args, step_name):
    """Run a pipeline step and return success status"""
    try:
        cmd = ["python", script_name] + args
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        st.success(f"✓ {step_name} completed")
        with st.expander(f"View {step_name} output"):
            st.code(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Error in {step_name}")
        st.code(e.stderr)
        return False


def main():
    """Main application"""
    st.set_page_config(
        page_title="Article Detective",
        page_icon="🔍",
        initial_sidebar_state="expanded",
        layout="wide"
    )

    st.title("🔍 Article Detective - Document Analysis")

    # Show environment info
    if "DOMINO_DATASETS_DIR" in os.environ:
        st.info(f"🏢 Running on Domino Data Lab")
    else:
        st.info(f"💻 Running locally")

    st.info(f"📁 Asset folder: `{ASSET_FOLDER}`")
    st.markdown("---")

    # Initialize session state
    if "asset_folder1" not in st.session_state:
        st.session_state.asset_folder1 = ""
    if "article_cleaned" not in st.session_state:
        st.session_state.article_cleaned = ""
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "to_execute" not in st.session_state:
        st.session_state.to_execute = False
    if "folder_name" not in st.session_state:
        st.session_state.folder_name = ""
    if "outputs_folder" not in st.session_state:
        st.session_state.outputs_folder = None

    # File upload section
    with st.form(key="upload_form", clear_on_submit=False):
        st.header("1. Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose your files",
            types=["docx", "pdf"],
            accept_multiple_files=True
        )
        submit = st.form_submit_button(label="Submit & Process")

        if submit and uploaded_files:
            st.session_state.uploaded_files = uploaded_files

            try:
                # Create folder structure
                if len(uploaded_files) == 1:
                    name_article, file_ext = os.path.splitext(uploaded_files[0].name)
                    folder_name = transform_string(name_article)
                else:
                    filenames = sorted([
                        transform_string(os.path.splitext(f.name)[0])
                        for f in uploaded_files
                    ])
                    unique_string = "_".join(filenames)
                    folder_hash = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()[:16]
                    folder_name = f"data_{folder_hash}"

                # Create directories
                folder_path = ASSET_FOLDER / "uploaded_documents" / folder_name
                folder_path.mkdir(parents=True, exist_ok=True)
                outputs_folder = folder_path / "outputs"
                outputs_folder.mkdir(parents=True, exist_ok=True)

                st.session_state.asset_folder1 = folder_path
                st.session_state.folder_name = folder_name
                st.session_state.outputs_folder = outputs_folder
                st.session_state.article_cleaned = folder_name

                # Save uploaded files
                file_paths = []
                for file in uploaded_files:
                    name_article, file_ext = os.path.splitext(file.name)
                    article_cleaned = transform_string(name_article)
                    file_path = folder_path / f"{article_cleaned}{file_ext}"

                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    file_paths.append(file_path)

                st.success(f"✓ {len(uploaded_files)} file(s) uploaded to `{folder_path}`")
                st.session_state.to_execute = True

            except Exception as e:
                st.error(f"Error during upload: {e}")
                st.session_state.to_execute = False

    # Process documents if uploaded
    if st.session_state.to_execute and st.session_state.uploaded_files:
        st.markdown("---")
        st.header("2. Processing Pipeline")

        outputs_folder = st.session_state.outputs_folder
        uploaded_files = st.session_state.uploaded_files

        # Run pipeline button
        if st.button("🚀 Run Analysis Pipeline", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            all_success = True
            folder_path = st.session_state.asset_folder1

            # Get file paths
            file_paths = []
            for file in uploaded_files:
                name_article, file_ext = os.path.splitext(file.name)
                article_cleaned = transform_string(name_article)
                file_path = folder_path / f"{article_cleaned}{file_ext}"
                file_paths.append(file_path)

            total_steps = 6
            current_step = 0

            # Process first file (or combined if multiple)
            file_path = file_paths[0]

            # Step 1: Summarize
            status_text.text("Step 1/6: Extracting text and summarizing...")
            if run_pipeline_step("step1_summarize.py", [str(file_path), str(outputs_folder)], "Step 1: Summarize"):
                current_step += 1
                progress_bar.progress(current_step / total_steps)
            else:
                all_success = False

            if all_success:
                # Step 2: Extract entities
                status_text.text("Step 2/6: Extracting entities...")
                if run_pipeline_step("step2_extract_entities.py", [str(outputs_folder)], "Step 2: Extract Entities"):
                    current_step += 1
                    progress_bar.progress(current_step / total_steps)
                else:
                    all_success = False

            if all_success:
                # Step 3: Describe entities
                status_text.text("Step 3/6: Describing entities...")
                if run_pipeline_step("step3_describe_entities.py", [str(outputs_folder)], "Step 3: Describe Entities"):
                    current_step += 1
                    progress_bar.progress(current_step / total_steps)
                else:
                    all_success = False

            if all_success:
                # Step 4: Group entities
                status_text.text("Step 4/6: Grouping similar entities...")
                if run_pipeline_step("step4_group_entities.py", [str(outputs_folder)], "Step 4: Group Entities"):
                    current_step += 1
                    progress_bar.progress(current_step / total_steps)
                else:
                    all_success = False

            if all_success:
                # Step 5: Analyze risks
                status_text.text("Step 5/6: Analyzing risks...")
                if run_pipeline_step("step5_analyze_risks.py", [str(outputs_folder)], "Step 5: Analyze Risks"):
                    current_step += 1
                    progress_bar.progress(current_step / total_steps)
                else:
                    all_success = False

            if all_success:
                # Step 6: Extract relationships
                status_text.text("Step 6/6: Extracting relationships...")
                if run_pipeline_step("step6_extract_relationships.py", [str(outputs_folder)], "Step 6: Extract Relationships"):
                    current_step += 1
                    progress_bar.progress(current_step / total_steps)
                else:
                    all_success = False

            if all_success:
                status_text.text("✅ All steps completed successfully!")
                progress_bar.progress(1.0)
                st.balloons()
            else:
                st.error("❌ Processing failed. Please check the errors above.")

        # Display results if outputs exist
        outputs_folder = st.session_state.outputs_folder

        # Check if analysis has been run
        if (outputs_folder / "summary.json").exists():
            st.markdown("---")
            st.header("3. Analysis Results")

            # Article Summary Section
            st.subheader("📄 Article Summary")
            try:
                with open(outputs_folder / "summary.json", "r") as f:
                    summary_data = json.load(f)
                st.write(summary_data["summary"])
            except Exception as e:
                st.error(f"Could not load summary: {e}")

            # Entities Section
            st.markdown("---")
            st.subheader("👥 Entities")

            try:
                with open(outputs_folder / "dict_unique_grouped_entity_summary.json", "r") as f:
                    dict_entity_summaries = json.load(f)

                entities = list(dict_entity_summaries.keys())

                # Entity selector
                selected_entity = st.selectbox("**Select an entity to view details**", entities)

                if selected_entity:
                    st.info("**Entity Description:**")
                    st.write(dict_entity_summaries[selected_entity])

                # Entities table
                with st.expander("View all entities"):
                    df_entities = pd.DataFrame([
                        {"Entity": name, "Description": desc[:200] + "..." if len(desc) > 200 else desc}
                        for name, desc in dict_entity_summaries.items()
                    ])
                    st.dataframe(df_entities, use_container_width=True)

            except Exception as e:
                st.error(f"Could not load entities: {e}")

            # Risk Assessment Section
            st.markdown("---")
            st.subheader("⚠️ Risk Assessment")

            try:
                with open(outputs_folder / "risk_assessment.json", "r") as f:
                    risks = json.load(f)

                flagged = risks.get("flagged_entities", [])
                if flagged:
                    st.warning(f"🚩 {len(flagged)} flagged entities found")
                    for entity in flagged:
                        with st.expander(f"🚩 {entity['entity_name']} - {entity['risk_level'].upper()} risk"):
                            st.write(f"**Crimes:** {', '.join(entity['crimes_flagged'])}")
                            st.write(f"**Confidence:** {entity['confidence']:.2f}")
                            st.write(f"**Evidence:**")
                            for evidence in entity['evidence']:
                                st.write(f"- {evidence}")
                            st.write(f"**Reasoning:** {entity['reasoning']}")
                else:
                    st.success("✅ No flagged entities")
            except Exception as e:
                st.error(f"Could not load risk assessment: {e}")

            # Knowledge Graph Section
            st.markdown("---")
            st.subheader("🔗 Entity Relationships & Knowledge Graph")

            try:
                # Load relationships
                with open(outputs_folder / "entity_relationships_filtered.json", "r") as f:
                    relationships = json.load(f)

                st.write(f"**Total relationships:** {len(relationships)}")

                # Display relationships table
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

                # Knowledge graph visualization
                if HAS_LINK_ANALYSIS:
                    st.markdown("**Interactive Knowledge Graph:**")
                    try:
                        with open(outputs_folder / "graph_elements.json", "r") as f:
                            elements = json.load(f)

                        edge_styles = [
                            EdgeStyle("Owner", caption='label', directed=False),
                            EdgeStyle("Investor", caption='label', directed=False),
                            EdgeStyle("Partner", caption='label', directed=False),
                            EdgeStyle("Shareholder", caption='label', directed=False),
                            EdgeStyle("Representative", caption='label', directed=False),
                            EdgeStyle("Beneficiary", caption='label', directed=False),
                            EdgeStyle("Other relationship", caption='label', directed=False)
                        ]

                        node_styles = [
                            NodeStyle("PERSON", "#FF7F3E", "name", "person"),
                            NodeStyle("FLAGGED", "#A155B9", "name", "flag")
                        ]

                        layout = {"name": "cose", "animate": "end", "nodeDimensionsIncludeLabels": False}

                        st_link_analysis(
                            elements,
                            node_styles=node_styles,
                            edge_styles=edge_styles,
                            layout=layout,
                            key="knowledge_graph"
                        )
                    except Exception as e:
                        st.error(f"Could not render knowledge graph: {e}")
                else:
                    st.info("💡 Tip: Install st_link_analysis for interactive graph visualization:\n`pip install streamlit-link-analysis`")

            except Exception as e:
                st.error(f"Could not load relationships: {e}")

            # Download section
            st.markdown("---")
            st.subheader("📥 Download Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                if (outputs_folder / "summary.json").exists():
                    with open(outputs_folder / "summary.json", "r") as f:
                        st.download_button(
                            "📄 Download Summary",
                            f.read(),
                            "summary.json",
                            "application/json"
                        )

            with col2:
                if (outputs_folder / "risk_assessment.json").exists():
                    with open(outputs_folder / "risk_assessment.json", "r") as f:
                        st.download_button(
                            "⚠️ Download Risk Assessment",
                            f.read(),
                            "risk_assessment.json",
                            "application/json"
                        )

            with col3:
                if (outputs_folder / "graph_elements.json").exists():
                    with open(outputs_folder / "graph_elements.json", "r") as f:
                        st.download_button(
                            "🔗 Download Knowledge Graph",
                            f.read(),
                            "graph_elements.json",
                            "application/json"
                        )


if __name__ == "__main__":
    main()
