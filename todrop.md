def dicts_to_text(class_list, output_file="people.txt"):
    lines = []
    for d in class_list:
        for person, attrs in d.items():
            lines.append(f"{person}:")
            if isinstance(attrs, dict):
                for k, v in attrs.items():
                    lines.append(f"  - {k}: {v}")
            lines.append("")  # blank line after each person

    # Join everything into a string
    text_output = "\n".join(lines)

    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text_output)

    return text_output


# Example usage
class_list = [
    {"Alice": {"age": 25, "city": "Paris", "address": "123 Main St"}},
    {"Bob": {"age": 30, "city": "London"}},
    {"Charlie": {"age": 40, "city": "Berlin", "address": "456 Park Ave"}}
]

txt = dicts_to_text(class_list, "people.txt")
print(txt)

