
# Update node labels
for node in graph['nodes']:
    entity_name = node['data']['name']
    
    # Determine entity type
    if entity_name in persons:
        entity_type = 'PERSON'
    elif entity_name in companies:
        entity_type = 'COMPANY'
    else:
        continue  # Skip unknown entities
    
    # Build label with optional suffix
    suffix = '_FLAGGED' if entity_name in flagged_entities else ''
    node['data']['label'] = f"{entity_type}{suffix}"
