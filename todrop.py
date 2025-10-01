
import json
import pandas as pd

# Load JSON
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Prepare rows for the DataFrame
rows = []
for entry in data:
    for person, info in entry.items():
        row = {"person": person}
        row.update(info)
        rows.append(row)

# Create DataFrame
df = pd.DataFrame(rows)

# Ensure the column order
df = df[["person", "age", "city"]]

# Save to Excel
df.to_excel("data.xlsx", index=False)

print("Saved data.xlsx with columns: person, age, city")
