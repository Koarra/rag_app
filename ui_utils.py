"""
UI Utility Functions for Streamlit Application
Contains reusable UI components for display and styling
"""
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
    """Display a beautiful progress UI with gradient background and animations"""
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    # Create unique class names to avoid CSS conflicts
    import random
    unique_id = f"prog_{random.randint(1000, 9999)}"

    progress_html = f"""
<style>
    @keyframes pulse_{unique_id} {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}

    .progress-wrapper-{unique_id} {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        text-align: center;
        margin: 20px 0;
    }}

    .progress-title-{unique_id} {{
        color: white;
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 10px;
        animation: pulse_{unique_id} 2s ease-in-out infinite;
    }}

    .progress-percentage-{unique_id} {{
        color: #fff;
        font-size: 48px;
        font-weight: 700;
        margin: 20px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}

    .progress-bar-container-{unique_id} {{
        background: rgba(255,255,255,0.2);
        border-radius: 50px;
        height: 20px;
        overflow: hidden;
        margin: 30px 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }}

    .progress-bar-fill-{unique_id} {{
        background: linear-gradient(90deg, #48c6ef 0%, #6f86d6 100%);
        height: 100%;
        width: {percentage}%;
        border-radius: 50px;
        transition: width 0.5s ease-in-out;
        box-shadow: 0 2px 10px rgba(72, 198, 239, 0.5);
    }}

    .progress-timer-{unique_id} {{
        color: rgba(255,255,255,0.9);
        font-size: 18px;
        font-weight: 500;
        margin-top: 15px;
        letter-spacing: 1px;
    }}

    .spinner-{unique_id} {{
        display: inline-block;
        margin-right: 10px;
        animation: pulse_{unique_id} 1.5s ease-in-out infinite;
    }}
</style>

<div class="progress-wrapper-{unique_id}">
    <div class="progress-title-{unique_id}">
        <span class="spinner-{unique_id}">🔄</span>
        Processing Your Documents
    </div>

    <div class="progress-percentage-{unique_id}">
        {percentage}%
    </div>

    <div class="progress-bar-container-{unique_id}">
        <div class="progress-bar-fill-{unique_id}"></div>
    </div>

    <div class="progress-timer-{unique_id}">
        ⏱️ {minutes:02d}:{seconds:02d}
    </div>
</div>
"""

    # Use the container to render HTML with markdown
    progress_container.markdown(progress_html, unsafe_allow_html=True)
