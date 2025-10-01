import json
import csv

# Load JSON
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Determine headers
inner_keys = list(next(iter(data[0].values())).keys())  # e.g., ['age', 'city']
fieldnames = ["person"] + inner_keys

# Write CSV with UTF-8 BOM so Excel reads it properly
with open("data.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()  # ensures first row is the header
    for entry in data:
        for person, info in entry.items():
            row = {"person": person}
            row.update(info)
            writer.writerow(row)

print("Saved to data.csv (Excel-friendly)")
