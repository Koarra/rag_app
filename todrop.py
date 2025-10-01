import csv
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

# 1️⃣ Load CSV data
csv_file = "data.csv"
data = []
with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        data.append(row)

# 2️⃣ Create a workbook and add data
wb = Workbook()
ws = wb.active
ws.title = "Sheet1"

for row in data:
    ws.append(row)

# 3️⃣ Define the table range
# Assuming the first row is headers
num_rows = len(data)
num_cols = len(data[0])
table_range = f"A1:{chr(64+num_cols)}{num_rows}"

# 4️⃣ Create a Table
table = Table(displayName="MyTable", ref=table_range)

# Optional: add style
style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                       showLastColumn=False, showRowStripes=True, showColumnStripes=True)
table.tableStyleInfo = style

# 5️⃣ Add table to worksheet
ws.add_table(table)

# 6️⃣ Save Excel file
wb.save("data.xlsx")
print("Saved data.xlsx with an Excel table!")
