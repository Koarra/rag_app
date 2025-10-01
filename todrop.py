import json
import csv

# Load JSON
with open("data.json", "r") as f:
    data = json.load(f)

# Determine headers (all keys except the person's name)
# Assuming all inner dictionaries have the same keys
inner_keys = list(next(iter(data[0].values())).keys())
fieldnames = ["person"] + inner_keys

# Write CSV
with open("data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for entry in data:
        # Each entry is like {"Jean": {"age": 25, "city": "NY"}}
        for person, info in entry.items():
            row = {"person": person}
            row.update(info)
            writer.writerow(row)

print("Saved to data.csv")
