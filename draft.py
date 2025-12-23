def calculate_crime_similarity(ref_entities: Dict, cur_entities: Dict) -> float:
    """
    Calculate crime recall based on matched entities only.
    Missing entities only affect entity recall, not crime recall.
    """
    total_matched_crimes = 0
    total_reference_crimes = 0
    
    # Get matched entity keys
    matched_keys = set(ref_entities.keys()) & set(cur_entities.keys())
    
    # If no entities matched, return 0
    if not matched_keys:
        return 0.0
    
    # Loop through ONLY matched entities
    for key in matched_keys:
        ref_crimes = set(ref_entities[key].get('crimes_flagged', []))
        cur_crimes = set(cur_entities[key].get('crimes_flagged', []))
        
        total_reference_crimes += len(ref_crimes)
        
        # Find matching crimes (set intersection)
        matched_crimes = ref_crimes & cur_crimes
        total_matched_crimes += len(matched_crimes)
    
    # Calculate crime recall for matched entities
    if total_reference_crimes == 0:
        return 1.0  # No crimes to detect in matched entities
    
    return total_matched_crimes / total_reference_crimes


Crime recall measures the proportion of reference crimes that are successfully identified for matched entities only. The calculation considers only entities that were detected in both reference and current outputs, then compares their crime labels using set intersection. This metric isolates crime classification performance from entity detection performance. The score is computed as total matched crimes divided by total reference crimes across matched entities.
