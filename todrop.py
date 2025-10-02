import csv
import os
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

def csv_to_excel_with_table(csv_path, excel_path):
    # Ensure input file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Load CSV data
    data = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)

    if not data:
        raise ValueError("CSV file is empty.")

    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    # Write data into sheet
    for row in data:
        ws.append(row)

    # Get table range
    num_rows = len(data)
    num_cols = len(data[0])
    table_range = f"A1:{chr(64 + num_cols)}{num_rows}"

    # Create table
    table = Table(displayName="MyTable", ref=table_range)
    style = TableStyleInfo(
        name="TableStyleMedium9",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=True,
    )
    table.tableStyleInfo = style
    ws.add_table(table)

    # Save workbook at the given path
    wb.save(excel_path)
    print(f"Excel file saved at: {excel_path}")
