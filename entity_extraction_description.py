from gliner import GLiNER
import os
from openai import OpenAI

# Force offline mode - prevents any connection to Hugging Face
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Initialize the GLiNER model from local directory
model = GLiNER.from_pretrained("./path/to/your/local/model", local_files_only=True)

# Initialize OpenAI client
client = OpenAI(api_key="your-api-key-here")

# Read your text file
with open("your_text_file.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Define the entity types you want to detect
labels = ["person", "organization", "location", "date", "product", "email", "phone number"]

# Predict entities
entities = model.predict_entities(text, labels, threshold=0.5)

# Extract unique entity texts into a list
entity_list = list(set([entity['text'] for entity in entities]))

print(f"Found {len(entity_list)} unique entities")
print(f"Entities: {entity_list}\n")


# Define simple JSON schema for structured output
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "entity_description",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "A brief description of the entity based on the context"
                }
            },
            "required": ["description"],
            "additionalProperties": False
        }
    }
}

# Generate descriptions for each entity using OpenAI
entity_descriptions = {}

for entity in entity_list:
    print(f"Generating description for: {entity}")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise descriptions of entities."},
                {"role": "user", "content": f"Provide a brief description of '{entity}' based on the following context:\n\n{text}\n\nDescription:"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        description = response.choices[0].message.content.strip()
        entity_descriptions[entity] = description
        
        print(f"Description: {description}\n")
        print("-" * 50)
        
    except Exception as e:
        print(f"Error generating description for {entity}: {e}")
        entity_descriptions[entity] = "Description not available"

# Display all results
print("\n" + "="*50)
print("FINAL RESULTS:")
print("="*50)
for entity, description in entity_descriptions.items():
    print(f"\nEntity: {entity}")
    print(f"Description: {description}")
    print("-" * 50)

# Optional: Save results to a file
with open("entity_descriptions.txt", "w", encoding="utf-8") as f:
    for entity, description in entity_descriptions.items():
        f.write(f"Entity: {entity}\n")
        f.write(f"Description: {description}\n")
        f.write("-" * 50 + "\n\n")
