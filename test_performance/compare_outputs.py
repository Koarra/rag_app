from typing import Dict, List, Tuple

def normalize_entity_key(entity: Dict) -> str:
    """Create unique key for entity matching"""
    return f"{entity['entity_name'].lower()}|{entity['entity_type'].lower()}"

def compare_outputs(reference: Dict, current: Dict) -> Dict:
    """Compare reference and current outputs, return metrics"""
    
    ref_entities = {normalize_entity_key(e): e for e in reference['flagged_entities']}
    cur_entities = {normalize_entity_key(e): e for e in current['flagged_entities']}
    
    # Metric 1: Entity Detection
    entity_similarity = calculate_entity_similarity(
        set(ref_entities.keys()), 
        set(cur_entities.keys())
    )
    
    # Metric 2: Crime Matching (for matched entities only)
    crime_similarity = calculate_crime_similarity(ref_entities, cur_entities)
    
    # Detailed breakdown
    matched = set(ref_entities.keys()) & set(cur_entities.keys())
    missing = set(ref_entities.keys()) - set(cur_entities.keys())
    extra = set(cur_entities.keys()) - set(ref_entities.keys())
    
    return {
        'entity_similarity': entity_similarity,
        'crime_similarity': crime_similarity,
        'entity_metrics': {
            'matched_count': len(matched),
            'missing_count': len(missing),
            'extra_count': len(extra),
            'missing_entities': [ref_entities[k]['entity_name'] for k in missing],
            'extra_entities': [cur_entities[k]['entity_name'] for k in extra]
        },
        'crime_details': get_crime_details(ref_entities, cur_entities, matched)
    }

def calculate_entity_similarity(ref_keys: set, cur_keys: set) -> float:
    """Jaccard similarity for entity sets"""
    if not ref_keys and not cur_keys:
        return 1.0
    
    intersection = len(ref_keys & cur_keys)
    union = len(ref_keys | cur_keys)
    return intersection / union if union > 0 else 0.0

def calculate_crime_similarity(ref_entities: Dict, cur_entities: Dict) -> float:
    """Average Jaccard similarity for crimes of matched entities"""
    matched_keys = set(ref_entities.keys()) & set(cur_entities.keys())
    
    if not matched_keys:
        return 0.0
    
    crime_scores = []
    for key in matched_keys:
        ref_crimes = set(ref_entities[key]['crimes_flagged'])
        cur_crimes = set(cur_entities[key]['crimes_flagged'])
        
        intersection = len(ref_crimes & cur_crimes)
        union = len(ref_crimes | cur_crimes)
        score = intersection / union if union > 0 else 0.0
        crime_scores.append(score)
    
    return sum(crime_scores) / len(crime_scores)

def get_crime_details(ref_entities: Dict, cur_entities: Dict, matched_keys: set) -> List[Dict]:
    """Detailed crime comparison for matched entities"""
    details = []
    
    for key in matched_keys:
        ref_crimes = set(ref_entities[key]['crimes_flagged'])
        cur_crimes = set(cur_entities[key]['crimes_flagged'])
        
        if ref_crimes != cur_crimes:
            details.append({
                'entity_name': ref_entities[key]['entity_name'],
                'expected_crimes': list(ref_crimes),
                'detected_crimes': list(cur_crimes),
                'missing_crimes': list(ref_crimes - cur_crimes),
                'extra_crimes': list(cur_crimes - ref_crimes)
            })
    
    return details