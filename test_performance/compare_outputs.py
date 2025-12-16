from typing import Dict, List, Set


def normalize_entity_key(entity: Dict) -> str:
    entity_name = entity.get('entity_name', '').lower().strip()
    entity_type = entity.get('entity_type', 'UNKNOWN').lower().strip()
    return f"{entity_name}|{entity_type}"


def calculate_entity_similarity(ref_keys: Set[str], cur_keys: Set[str]) -> float:
    if not ref_keys and not cur_keys:
        return 1.0

    intersection = len(ref_keys & cur_keys)
    union = len(ref_keys | cur_keys)
    return intersection / union if union > 0 else 0.0


def calculate_crime_similarity(ref_entities: Dict, cur_entities: Dict) -> float:
    matched_keys = set(ref_entities.keys()) & set(cur_entities.keys())

    if not matched_keys:
        return 0.0

    crime_scores = []
    for key in matched_keys:
        ref_crimes = set(ref_entities[key].get('crimes_flagged', []))
        cur_crimes = set(cur_entities[key].get('crimes_flagged', []))

        intersection = len(ref_crimes & cur_crimes)
        union = len(ref_crimes | cur_crimes)
        score = intersection / union if union > 0 else 0.0
        crime_scores.append(score)

    return sum(crime_scores) / len(crime_scores) if crime_scores else 0.0


def get_crime_details(ref_entities: Dict, cur_entities: Dict, matched_keys: Set[str]) -> List[Dict]:
    details = []

    for key in matched_keys:
        ref_crimes = set(ref_entities[key].get('crimes_flagged', []))
        cur_crimes = set(cur_entities[key].get('crimes_flagged', []))

        if ref_crimes != cur_crimes:
            details.append({
                'entity_name': ref_entities[key]['entity_name'],
                'expected_crimes': sorted(list(ref_crimes)),
                'detected_crimes': sorted(list(cur_crimes)),
                'missing_crimes': sorted(list(ref_crimes - cur_crimes)),
                'extra_crimes': sorted(list(cur_crimes - ref_crimes))
            })

    return details


def compare_outputs(reference: Dict, current: Dict) -> Dict:
    # Normalize entities for comparison
    ref_entities = {
        normalize_entity_key(e): e
        for e in reference.get('flagged_entities', [])
    }
    cur_entities = {
        normalize_entity_key(e): e
        for e in current.get('flagged_entities', [])
    }

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
            'reference_total': len(ref_entities),
            'current_total': len(cur_entities),
            'missing_entities': [ref_entities[k]['entity_name'] for k in missing],
            'extra_entities': [cur_entities[k]['entity_name'] for k in extra]
        },
        'crime_details': get_crime_details(ref_entities, cur_entities, matched)
    }
