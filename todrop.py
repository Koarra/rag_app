import json
import csv

# Load JSON
with open("data.json", "r") as f:
    data = json.load(f)

# Determine CSV headers
fieldnames = ["person"] + list(next(iter(data.values())).keys())

# Write CSV
with open("data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for person, info in data.items():
        row = {"person": person}
        row.update(info)
        writer.writerow(row)

print("Saved to data.csv")
