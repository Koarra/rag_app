import json
import csv

# Load JSON list
with open("data.json", "r") as f:
    data = json.load(f)

# Check if data is a list
if not isinstance(data, list):
    raise ValueError("Expected a list of dictionaries in data.json")

# Determine headers
# Let's make "person" the 'name' field
fieldnames = ["person"] + [key for key in data[0] if key != "name"]

# Write CSV
with open("data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for entry in data:
        row = {"person": entry.get("name", "")}  # map 'name' -> 'person'
        for key, value in entry.items():
            if key != "name":
                row[key] = value
        writer.writerow(row)

print("Saved to data.csv")
