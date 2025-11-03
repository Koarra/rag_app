"""
UI Utility Functions for Streamlit Application
Contains reusable UI components for display and styling
"""
import streamlit as st
import streamlit.components.v1 as components


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


def show_beautiful_progress(progress_container, percentage, elapsed_time):
    """Display a simple progress UI using native Streamlit components"""
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    with progress_container.container():
        # Title
        st.markdown("### 🔄 Processing Your Documents")

        # Percentage as metric
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.metric(label="Progress", value=f"{percentage}%", delta=None)

        # Progress bar
        st.progress(percentage / 100.0)

        # Timer
        st.caption(f"⏱️ Elapsed time: {minutes:02d}:{seconds:02d}")
