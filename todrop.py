import json
import csv
import os
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

def json_to_excel_with_table(data_dict, excel_path):
    # Validate input data
    if not data_dict:
        raise ValueError("Dictionary is empty.")
    
    # Determine headers (all keys except the "person" key)
    inner_keys = list(next(iter(data_dict.values())).keys())
    fieldnames = ["person"] + inner_keys
    
    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    
    # Write headers
    ws.append(fieldnames)
    
    # Write data rows
    for person, info in data_dict.items():
        row = [person] + [info.get(k, "") for k in inner_keys]
        ws.append(row)
    
    # Define table range
    num_rows = ws.max_row
    num_cols = ws.max_column
    
    # Handle Excel-style column naming beyond Z
    def col_letter(n):
        result = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            result = chr(65 + remainder) + result
        return result
    
    table_range = f"A1:{col_letter(num_cols)}{num_rows}"
    
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
    
    # Save Excel
    wb.save(excel_path)
    print(f"Excel file saved at: {excel_path}")
