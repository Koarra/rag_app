leaned_content = re.sub(r'^```json\s*|\s*```$', '', content.strip(), flags=re.MULTILINE)

# Now parse the JSON
try:
    data = json.loads(cleaned_content)
    print(data)
except json.JSONDecodeError as e:
    print(f"JSON parsing error: {e}")
    print(f"Content was: {cleaned_content}")
