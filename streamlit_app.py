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
import streamlit.components.v1 as components
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
from ui_utils import define_html, show_beautiful_progress

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


def transform_string(input_string):
    """Transform string for use as filename or folder name."""
    cleaned = re.sub(r'[^\w\s-]', '', input_string)
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned.lower()


def run_step(script_name, args):
    """Run a step script with output visible in terminal"""
    try:
        cmd = ["python", script_name] + args

        # Let stdout/stderr flow through to terminal instead of capturing
        result = subprocess.run(
            cmd,
            text=True,
            check=True
        )

        return True, "", ""
    except subprocess.CalledProcessError as e:
        return False, "", str(e)


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

    # File upload section with two-column layout
    st.header("📤 Upload Documents")

    # Add custom CSS for boxes
    st.markdown("""
    <style>
    .upload-box {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background-color: #f9f9f9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
    }
    .info-box {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background-color: #f0f7ff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

    col_upload, col_info = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        st.markdown("#### 📁 Select Files")
        uploaded_files = st.file_uploader(
            "Drag and drop or browse",
            type=["docx", "pdf"],
            accept_multiple_files=True,
            help="Upload one or more PDF or DOCX files for analysis",
            label_visibility="collapsed"
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("#### 📋 Document Information")
        if uploaded_files:
            # Show document details
            total_size = sum(f.size for f in uploaded_files)
            total_size_mb = total_size / (1024 * 1024)

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Total Files", len(uploaded_files))
            with col_m2:
                st.metric("Total Size", f"{total_size_mb:.2f} MB")

            st.markdown("---")

            # Show file list with details
            st.markdown("**📄 File List:**")
            for i, file in enumerate(uploaded_files, 1):
                file_size_kb = file.size / 1024
                file_type = "📕 PDF" if file.name.endswith('.pdf') else "📘 DOCX"
                st.markdown(f"**{i}.** {file.name}")
                st.caption(f"   {file_type} • {file_size_kb:.1f} KB")
        else:
            st.info("👈 Upload documents to see details here")
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_files:

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

            # Create outputs subfolder
            outputs_folder = output_folder / "outputs"
            outputs_folder.mkdir(parents=True, exist_ok=True)

            # Store in session state
            st.session_state.outputs_folder = outputs_folder

            all_success = True
            errors = []

            # Process all files through step 1
            total_steps = len(file_paths) + 5  # Files + 5 remaining steps
            current_step = 0

            # Beautiful progress display container
            progress_container = st.empty()

            for file_path in file_paths:
                current_step += 1
                progress = current_step / total_steps
                elapsed = time.time() - start_time

                show_beautiful_progress(progress_container, int(progress * 100), elapsed)

                success, stdout, stderr = run_step("step1_summarize.py", [str(file_path), str(outputs_folder)])
                if not success:
                    all_success = False
                    errors.append(f"Step 1 failed for {file_path.name}: {stderr}")
                    break

            # Run remaining steps once (they process all entities together)
            if all_success:
                steps = [
                    ("step2_extract_entities.py", "Extracting entities"),
                    ("step3_describe_entities.py", "Describing entities"),
                    ("step4_group_entities.py", "Grouping similar entities"),
                    ("step5_analyze_risks.py", "Analyzing risks"),
                    ("step6_extract_relationships.py", "Extracting relationships")
                ]

                for script, message in steps:
                    current_step += 1
                    progress = current_step / total_steps
                    elapsed = time.time() - start_time

                    show_beautiful_progress(progress_container, int(progress * 100), elapsed)

                    success, stdout, stderr = run_step(script, [str(outputs_folder)])
                    if not success:
                        all_success = False
                        errors.append(f"{script} failed: {stderr}")
                        break

            # Calculate final processing time
            end_time = time.time()
            processing_time = end_time - start_time
            minutes = int(processing_time // 60)
            seconds = int(processing_time % 60)

            # Clear progress display
            progress_container.empty()

            if all_success:
                st.success(f"✅ Processing completed in {minutes:02d}:{seconds:02d}")
                st.session_state.results_ready = True
                st.balloons()
            else:
                st.error(f"❌ Processing failed after {minutes:02d}:{seconds:02d}")
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

                    # Build activities table data - ONLY FLAGGED ENTITIES
                    activities_data = []
                    for entity_name, description in entities.items():
                        # Check if entity is flagged
                        is_flagged = entity_name in entity_crimes

                        # ONLY ADD FLAGGED ENTITIES TO THE TABLE
                        if not is_flagged:
                            continue

                        # Build summary (description + reasoning)
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
                        entity_crime_set = entity_crimes[entity_name]['crimes']
                        for crime in CRIME_CATEGORIES:
                            row[crime] = crime in entity_crime_set

                        activities_data.append(row)

                    # Create DataFrame
                    df_activities = pd.DataFrame(activities_data)

                    # Initialize session state for edit mode and edited data
                    if 'edit_mode_table' not in st.session_state:
                        st.session_state.edit_mode_table = False
                    if 'edited_activities_df' not in st.session_state:
                        st.session_state.edited_activities_df = df_activities.copy()

                    # Filter to show only flagged entities
                    df_display = st.session_state.edited_activities_df[st.session_state.edited_activities_df['Flagged'] == True].copy()

                    # Display stats
                    st.write(f"**Total flagged entities: {len(df_display)}**")

                    # Check if there are any flagged entities to display
                    if len(df_display) == 0:
                        st.info("ℹ️ No flagged entities to display. All entities have been unflagged.")
                    else:
                        # Filter crime columns - only show columns where at least one entity has it flagged
                        active_crime_columns = [crime for crime in CRIME_CATEGORIES if df_display[crime].any()]

                        # Show info about hidden columns
                        hidden_columns = [crime for crime in CRIME_CATEGORIES if crime not in active_crime_columns]
                        if hidden_columns:
                            st.caption(f"ℹ️ Hidden columns (no entities flagged): {', '.join([c.replace('_', ' ').title() for c in hidden_columns])}")

                        # Column selector - allow user to select which crime columns to display
                        with st.expander("🎛️ Select Crime Columns to Display", expanded=False):
                            # Initialize selected columns in session state
                            if 'selected_crime_columns' not in st.session_state:
                                st.session_state.selected_crime_columns = active_crime_columns.copy()

                            # Update selected columns if active columns changed (e.g., after editing)
                            # Keep only columns that are still active
                            st.session_state.selected_crime_columns = [
                                col for col in st.session_state.selected_crime_columns
                                if col in active_crime_columns
                            ]
                            # If no columns left, default to all active
                            if not st.session_state.selected_crime_columns:
                                st.session_state.selected_crime_columns = active_crime_columns.copy()

                            # Multiselect for crime columns
                            selected_columns = st.multiselect(
                                "Choose which crime categories to display:",
                                options=active_crime_columns,
                                default=st.session_state.selected_crime_columns,
                                format_func=lambda x: x.replace("_", " ").title(),
                                key="crime_column_selector"
                            )

                            # Update session state with current selection
                            st.session_state.selected_crime_columns = selected_columns if selected_columns else active_crime_columns

                        # Use selected columns for display
                        display_crime_columns = st.session_state.selected_crime_columns

                        # Edit/View toggle buttons
                        col1, col2, col3, col4 = st.columns([1, 1, 1, 7])
                        with col1:
                            if st.button("✏️ Edit Table" if not st.session_state.edit_mode_table else "👁️ View Table"):
                                st.session_state.edit_mode_table = not st.session_state.edit_mode_table
                                st.rerun()

                        with col2:
                            if st.session_state.edit_mode_table:
                                if st.button("💾 Save Changes"):
                                    # Save the edited data - need to restore full dataframe with all columns
                                    # Update only the rows that were in df_display
                                    for idx in st.session_state.temp_edited_df.index:
                                        st.session_state.edited_activities_df.loc[idx] = st.session_state.temp_edited_df.loc[idx]
                                    st.toast("✅ Changes saved successfully!")
                                    st.rerun()

                        with col3:
                            if st.button("🔄 Reset Table"):
                                # Reset to original data from files
                                st.session_state.edited_activities_df = df_activities.copy()
                                st.toast("⚠️ Table reset to original data")
                                st.rerun()

                        # Display mode: Edit or View
                        if st.session_state.edit_mode_table:
                            # EDIT MODE: Show editable data editor
                            st.info("🔓 **Edit Mode Active** - You can now edit any cell in the table below. Click 'Save Changes' when done.")

                            # Reorder columns for better editing experience - use selected crime columns
                            cols_to_exclude = ["Entity", "Summary", "Comments", "Flagged"]
                            desired_order = cols_to_exclude + display_crime_columns
                            df_to_edit = df_display[desired_order]

                            # Configure column display
                            column_config = {
                                "Entity": st.column_config.TextColumn("Entity", width="medium", disabled=True),
                                "Summary": st.column_config.TextColumn("Summary", width="large"),
                                "Comments": st.column_config.TextColumn("Comments", width="large"),
                                "Flagged": st.column_config.CheckboxColumn("Flagged", width="small"),
                            }

                            # Add checkbox config for selected crime columns only
                            for crime in display_crime_columns:
                                column_config[crime] = st.column_config.CheckboxColumn(
                                    crime.replace("_", " ").title(),
                                    width="small"
                                )

                            # Show editable dataframe
                            edited_df = st.data_editor(
                                df_to_edit,
                                use_container_width=True,
                                height=600,
                                column_config=column_config,
                                hide_index=True,
                                key="activities_editor"
                            )

                            # Store temporarily for saving
                            st.session_state.temp_edited_df = edited_df

                        else:
                            # VIEW MODE: Show custom HTML table with styling
                            # Function to apply checkmarks and crosses
                            def apply_checkmarks(val):
                                if isinstance(val, bool):
                                    if val:
                                        return '<span style="color: green; font-size: 18px;">✓</span>'
                                    else:
                                        return '<span style="color: red; font-size: 18px;">✗</span>'
                                return val

                            # Apply styling to boolean columns - use selected crime columns
                            styled_df = df_display[["Entity", "Summary", "Comments", "Flagged"] + display_crime_columns].copy()
                            boolean_columns = ["Flagged"] + display_crime_columns

                            for col in boolean_columns:
                                styled_df[col] = styled_df[col].apply(apply_checkmarks)

                            # Prepare DataFrame for HTML table - reorder columns
                            cols_to_exclude = ["Entity", "Summary", "Comments", "Flagged"]
                            col_boolean_wo_flagged_list = display_crime_columns

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

                            # Display the custom HTML table using components.html for proper rendering
                            components.html(html_table, height=950, scrolling=True)

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
