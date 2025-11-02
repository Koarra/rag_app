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
from database_utils import save_to_database, create_dataframe_from_results

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

# Database configuration
SQLITE_DB_PATH = ASSET_FOLDER / "articledetective_feedback.db"
DUCKDB_DB_PATH = ASSET_FOLDER / "articledetective_feedback.duckdb"


def define_html(filtered_df, cols_to_exclude, col_boolean_list):
    """Generate custom HTML table with styled headers"""

    # Build table rows
    rows_html = []
    for row in filtered_df.values:
        cells = []
        for col, cell in zip(filtered_df.columns, row):
            if col in col_boolean_list:
                cells.append(f'<td class="boolean-column">{cell}</td>')
            else:
                cells.append(f'<td>{cell}</td>')
        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    rows_str = " ".join(rows_html)

    # Build crime column headers
    crime_headers = " ".join(
        f"<th class='rotate-header'>{col}</th>"
        for col in filtered_df.columns
        if col not in cols_to_exclude
    )

    html_string = f"""
    <style>
        .table-container {{
            width: 100%;
            height: 900px; /* Ensure a fixed height for the container */
            overflow-x: auto;  /* Always show horizontal scrollbar */
            overflow-y: auto;  /* Always show vertical scrollbar */
        }}
        table.custom-table {{
            border-collapse: collapse;
            width: 99%;  /* Set table width to 99% */
            table-layout: auto; /* Allow table to automatically adjust column widths */
        }}
        thead {{
            position: sticky;
            top: 0;
            z-index: 10;
            backdrop-filter: blur(8px);
        }}
        th, td {{
            min-width: 50px; /* Adjust the minimum column width as needed */
            max-width: 300px;
            max-height: 20px;
            padding: 50px;
            overflow: hidden;
            text-overflow: nowrap; /* Increased padding for better visibility */
        }}
        .boolean-column {{
            min-width: 10px;
            max-width: 20px;
            text-align: center;
        }}
        /* Add vertical space between header and first row */
        th {{
            padding-bottom: 50px; /* Adjust this value to increase/decrease spacing */
        }}
        th.rotate-header {{
            writing-mode: vertical-rl;
            transform: rotate(205deg);
            vertical-align: bottom;
            text-align: center;
            height: 250px; /* Adjusted height */
            white-space: normal;  /* Allow text to break into multiple lines */
            word-wrap: break-word; /* Ensure long text breaks */
            max-width: 500px;  /* Adjust this value to control how long text can be before wrapping */
        }}
        th.first-column-header {{
            writing-mode: horizontal-tb; /* Keep the first column header horizontal */
            text-align: center;
            height: 5px;
            max-width: 15px;
            vertical-align: bottom;
        }}
        /* Custom style for second column (Summary) */
        th.second-column-header {{
            writing-mode: horizontal-tb; /* Keep the first column header horizontal */
            text-align: center;
            height: 5px;
            max-width: 15px;
            vertical-align: bottom;
        }}
        /* Custom style for third column (Comments) */
        th.third-column-header {{
            writing-mode: horizontal-tb; /* Keep the first column header horizontal */
            text-align: center;
            height: 5px;
            max-width: 500px;
            vertical-align: bottom;
        }}
        /* Custom style for fourth column (Flagged) */
        th.fourth-column-header {{
            writing-mode: vertical-tb; /* Keep the first column header horizontal */
            text-align: center;
            height: 5px;
            max-width: 100px;
            vertical-align: bottom;
        }}
        td {{
            border: 1px solid #dddddd;
            text-align: center;
            font-size: 14px;  /* Increased font size for better visibility */
        }}
        /* Freeze the first column */
        td:first-child, th:first-child {{
            z-index: 1; /* Ensure it appears above other cells when scrolling */
        }}
        /* Freeze the second column */
        td:nth-child(2), th:nth-child(2) {{
            z-index: 1;
        }}
        /* Freeze the third column */
        td:nth-child(3), th:nth-child(3) {{
            z-index: 1;
        }}
    </style>
    <div class="table-container">
        <table class="custom-table">
            <thead>
                <tr>
                    <th class="first-column-header">Entity</th>
                    <th class="second-column-header">Summary</th>
                    <th class="third-column-header">Comments</th>
                    <th class="fourth-column-header">Flagged</th>
                    {crime_headers}
                </tr>
            </thead>
            <tbody>
                {rows_str}
            </tbody>
        </table>
    </div>
    """
    return html_string


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

    st.title("🔍 Article Detective")

    # Show environment info
    if "DOMINO_DATASETS_DIR" in os.environ:
        st.info(f"🏢 Running on Domino Data Lab - Output folder: `{ASSET_FOLDER}`")
    else:
        st.info(f"💻 Running locally - Output folder: `{ASSET_FOLDER}`")

    st.markdown("---")

    # File upload section
    st.header("Upload Documents")
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
        file_paths = []
        for uploaded_file in uploaded_files:
            name_article, file_ext = Path(uploaded_file.name).stem, Path(uploaded_file.name).suffix
            article_cleaned = transform_string(name_article)
            file_path = output_folder / f"{article_cleaned}{file_ext}"

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)

        st.markdown("---")

        # Initialize session state for results
        if 'results_ready' not in st.session_state:
            st.session_state.results_ready = False
        if 'outputs_folder' not in st.session_state:
            st.session_state.outputs_folder = None

        # Process documents button
        if st.button("🚀 Process Documents", type="primary"):
            # Track processing time
            import time
            start_time = time.time()

            # Create a placeholder for dynamic updates
            processing_placeholder = st.empty()
            timer_placeholder = st.empty()

            # Create outputs subfolder
            outputs_folder = output_folder / "outputs"
            outputs_folder.mkdir(parents=True, exist_ok=True)

            # Store in session state
            st.session_state.outputs_folder = outputs_folder

            all_success = True
            errors = []

            # Cool processing animation with real-time timer
            def update_processing_status(message, step=None, total_steps=None):
                elapsed = time.time() - start_time
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)

                if step and total_steps:
                    progress = step / total_steps
                    progress_bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
                    status_msg = f"### 🔄 {message}\n\n`[{progress_bar}]` Step {step}/{total_steps}\n\n⏱️ **Elapsed time: {minutes:02d}:{seconds:02d}**"
                else:
                    status_msg = f"### 🔄 {message}\n\n⏱️ **Elapsed time: {minutes:02d}:{seconds:02d}**"

                processing_placeholder.markdown(status_msg)

            # Process all files through step 1
            total_steps = len(file_paths) + 5  # Files + 5 remaining steps
            current_step = 0

            for file_path in file_paths:
                current_step += 1
                update_processing_status(f"Extracting text from {file_path.name}...", current_step, total_steps)
                success, stdout, stderr = run_step("step1_summarize.py", [str(file_path), str(outputs_folder)])
                if not success:
                    all_success = False
                    errors.append(f"Step 1 failed for {file_path.name}: {stderr}")
                    break

            # Run remaining steps once (they process all entities together)
            if all_success:
                steps = [
                    ("step2_extract_entities.py", "Extracting entities..."),
                    ("step3_describe_entities.py", "Describing entities..."),
                    ("step4_group_entities.py", "Grouping similar entities..."),
                    ("step5_analyze_risks.py", "Analyzing risks..."),
                    ("step6_extract_relationships.py", "Extracting relationships...")
                ]

                for script, message in steps:
                    current_step += 1
                    update_processing_status(message, current_step, total_steps)
                    success, stdout, stderr = run_step(script, [str(outputs_folder)])
                    if not success:
                        all_success = False
                        errors.append(f"{script} failed: {stderr}")
                        break

            # Calculate final processing time
            end_time = time.time()
            processing_time = end_time - start_time

            # Clear processing message
            processing_placeholder.empty()
            timer_placeholder.empty()

            if all_success:
                st.success(f"✅ Processing completed successfully in {processing_time:.2f} seconds")
                st.session_state.results_ready = True
                st.balloons()
            else:
                st.error(f"❌ Processing failed after {processing_time:.2f} seconds")
                st.session_state.results_ready = False
                if errors:
                    st.subheader("Error Details")
                    for error in errors:
                        st.code(error)

        # Display results section (outside button handler so it persists across reruns)
        if st.session_state.results_ready and st.session_state.outputs_folder:
            outputs_folder = st.session_state.outputs_folder

            st.markdown("---")

            # ============================================
            # Section 1: Article Summary
            # ============================================
            with st.container():
                st.header("📄 Article Summary")

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
            # Section 2: Activities Table
            # ============================================
            st.markdown("---")
            with st.container():
                st.header("📊 Activities Table")

                try:
                    with open(outputs_folder / "dict_unique_grouped_entity_summary.json", "r") as f:
                        entities = json.load(f)

                    with open(outputs_folder / "risk_assessment.json", "r") as f:
                        risks = json.load(f)

                    # Create a mapping of entities to their crime flags and reasoning
                    entity_crimes = {}
                    for flagged_entity in risks.get("flagged_entities", []):
                        entity_name = flagged_entity['entity_name']
                        entity_crimes[entity_name] = {
                            'crimes': set(flagged_entity['crimes_flagged']),
                            'reasoning': flagged_entity['reasoning']
                        }

                    # List of all crime types (from database_utils.py)
                    CRIME_CATEGORIES = [
                        "money_laundering",
                        "sanctions_evasion",
                        "terrorist_financing",
                        "bribery",
                        "corruption",
                        "embezzlement",
                        "fraud",
                        "tax_evasion",
                        "insider_trading",
                        "market_manipulation",
                        "ponzi_scheme",
                        "pyramid_scheme",
                        "identity_theft",
                        "cybercrime",
                        "human_trafficking"
                    ]

                    # Build activities table data
                    activities_data = []
                    for entity_name, description in entities.items():
                        # Check if entity is flagged
                        is_flagged = entity_name in entity_crimes

                        # Build summary (description + reasoning if flagged)
                        summary = description
                        if is_flagged:
                            reasoning = entity_crimes[entity_name]['reasoning']
                            summary = f"{description}\n\nReason: {reasoning}"

                        # Create row data
                        row = {
                            "Entity": entity_name,
                            "Summary": summary,
                            "Comments": "",  # Empty comments field
                            "Flagged": is_flagged
                        }

                        # Add crime columns
                        if is_flagged:
                            entity_crime_set = entity_crimes[entity_name]['crimes']
                            for crime in CRIME_CATEGORIES:
                                row[crime] = crime in entity_crime_set
                        else:
                            for crime in CRIME_CATEGORIES:
                                row[crime] = False

                        activities_data.append(row)

                    # Create DataFrame
                    df_activities = pd.DataFrame(activities_data)

                    # Function to apply checkmarks and crosses
                    def apply_checkmarks(val):
                        if isinstance(val, bool):
                            if val:
                                return '<span style="color: green; font-size: 18px;">✓</span>'
                            else:
                                return '<span style="color: red; font-size: 18px;">✗</span>'
                        return val

                    # Apply styling to boolean columns
                    styled_df = df_activities.copy()
                    boolean_columns = ["Flagged"] + CRIME_CATEGORIES

                    for col in boolean_columns:
                        styled_df[col] = styled_df[col].apply(apply_checkmarks)

                    # Display the table
                    st.write(f"**Total entities: {len(activities_data)}**")
                    st.write(f"**Flagged entities: {sum(1 for row in activities_data if row['Flagged'])}**")

                    # Prepare DataFrame for HTML table - reorder columns
                    cols_to_exclude = ["Entity", "Summary", "Comments", "Flagged"]
                    col_boolean_wo_flagged_list = CRIME_CATEGORIES

                    # Get all columns and reorder: fixed columns first, then crime columns
                    all_cols = list(styled_df.columns)
                    for column in cols_to_exclude:
                        if column in all_cols:
                            all_cols.remove(column)

                    # Desired order: Entity, Summary, Comments, Flagged, then crime columns
                    desired_cols = cols_to_exclude + all_cols
                    filtered_df = styled_df[desired_cols]

                    # Generate custom HTML table
                    html_table = define_html(filtered_df, cols_to_exclude, col_boolean_wo_flagged_list)

                    # Display the custom HTML table using st.html (not st.markdown!)
                    st.html(html_table)

                except Exception as e:
                    st.error(f"Could not load activities table: {e}")

            # ============================================
            # Section 3: Entity Relationships (Graph)
            # ============================================
            st.markdown("---")
            with st.container():
                st.header("🔗 Entity Relationships")

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

                    # Show relationships table below graph
                    st.markdown("---")
                    st.subheader("Relationship Details")

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
                    st.error(f"Could not load knowledge graph: {e}")

            # ============================================
            # Section 4: Entity Summaries
            # ============================================
            st.markdown("---")
            with st.container():
                st.header("👥 Entity Summaries")

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
            # Section 5: Save to Database
            # ============================================
            st.markdown("---")
            with st.container():
                st.header("💾 Save Results to Database")

                st.info("Save your analysis results to the database for tracking and history.")

                # Initialize session state for comments
                if 'entity_comments' not in st.session_state:
                    st.session_state.entity_comments = {}

                # Load entities for commenting
                try:
                    with open(outputs_folder / "dict_unique_grouped_entity_summary.json", "r") as f:
                        entities = json.load(f)

                    with open(outputs_folder / "risk_assessment.json", "r") as f:
                        risk_assessment = json.load(f)

                    # Allow adding comments to entities
                    with st.expander("Add Comments to Entities (Optional)"):
                        st.write("Add comments or notes for specific entities before saving:")

                        for entity_name in list(entities.keys())[:10]:  # Show first 10 entities
                            comment = st.text_input(
                                f"Comment for **{entity_name}**:",
                                value=st.session_state.entity_comments.get(entity_name, ""),
                                key=f"comment_{entity_name}"
                            )
                            st.session_state.entity_comments[entity_name] = comment

                    # Save button
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.button("💾 Save to Database", type="primary"):
                            # Create DataFrame from results
                            df = create_dataframe_from_results(
                                entities,
                                risk_assessment,
                                st.session_state.entity_comments
                            )

                            # Generate table name from folder
                            folder_name = outputs_folder.parent.name
                            table_name = f"entities_{re.sub(r'[^a-zA-Z0-9]', '_', folder_name)}"

                            # Get or create session ID
                            if 'session_id' not in st.session_state:
                                st.session_state.session_id = hashlib.sha256(
                                    str(datetime.now()).encode()
                                ).hexdigest()[:16]

                            # Save to database
                            success, message = save_to_database(
                                df,
                                table_name,
                                st.session_state.session_id,
                                SQLITE_DB_PATH,
                                DUCKDB_DB_PATH
                            )

                            if success:
                                st.success(message)
                                st.balloons()
                            else:
                                st.error(message)

                    with col2:
                        st.caption(f"Session ID: {st.session_state.get('session_id', 'Not generated')}")
                        st.caption(f"SQLite: {SQLITE_DB_PATH}")
                        st.caption(f"DuckDB: {DUCKDB_DB_PATH}")

                except Exception as e:
                    st.error(f"Could not prepare database save: {e}")


if __name__ == "__main__":
    main()
