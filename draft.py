def calculate_crime_similarity(ref_entities: Dict, cur_entities: Dict) -> float:
    total_matched_crimes = 0
    total_reference_crimes = 0
    
    # Loop through ALL reference entities (not just matched ones)
    for key, ref_entity in ref_entities.items():
        ref_crimes = set(ref_entity.get('crimes_flagged', []))
        total_reference_crimes += len(ref_crimes)
        
        # Check if entity exists in current output
        if key in cur_entities:
            cur_crimes = set(cur_entities[key].get('crimes_flagged', []))
            matched_crimes = ref_crimes & cur_crimes
            total_matched_crimes += len(matched_crimes)
        # else: entity missing → 0 matched crimes (implicit)
    
    # Calculate recall: matched / reference
    if total_reference_crimes == 0:
        return 1.0  # No crimes to detect
    
    return total_matched_crimes / total_reference_crimes
