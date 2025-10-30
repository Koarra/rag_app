"""
Name matching utilities for fuzzy partner name matching.
"""
import re
import json
from datetime import datetime
from difflib import SequenceMatcher


def normalize_name(name):
    """
    Normalize a name for matching by:
    1. Converting to lowercase
    2. Removing all non-letter characters (but keeping all alphabets from any language)
    3. Splitting into words and sorting alphabetically
    
    Args:
        name (str): The name to normalize
        
    Returns:
        str: Normalized name with words sorted alphabetically
        
    Examples:
        >>> normalize_name("Smith_John_2024")
        'john smith'
        >>> normalize_name("García López, María")
        'garcía lópez maría'
        >>> normalize_name("JOHN SMITH")
        'john smith'
    """
    if not name:
        return ""
    
    # Convert to lowercase
    name_lower = name.lower()
    
    # Keep only letters (supports Unicode letters from all languages)
    words = re.findall(r'\w+', name_lower, re.UNICODE)
    
    # Filter to keep only words that contain letters (removes pure numbers)
    words = [word for word in words if re.search(r'[a-zà-ÿα-ωа-я]', word, re.IGNORECASE | re.UNICODE)]
    
    # Sort alphabetically
    words_sorted = sorted(words)
    
    # Join back together
    return ' '.join(words_sorted)


def fuzzy_match_name(target_name, candidate_names, threshold=0.8):
    """
    Match a target name with a list of candidate names using fuzzy matching.
    
    This function normalizes names (lowercase, removes special chars, sorts words)
    and uses sequence matching to find the best match above a similarity threshold.
    
    Args:
        target_name (str): The name to match
        candidate_names (list): List of candidate names to match against
        threshold (float): Similarity threshold (0.0 to 1.0), default 0.8 (80%)
        
    Returns:
        tuple: (matched_name, similarity_score) if match found above threshold,
               (None, best_score) if no match found
               
    Examples:
        >>> candidates = ["John Smith", "Maria Garcia", "Robert Johnson"]
        >>> fuzzy_match_name("Smith_John_2024", candidates)
        ('John Smith', 1.0)
        >>> fuzzy_match_name("Garcia Maria", candidates)
        ('Maria Garcia', 1.0)
        >>> fuzzy_match_name("Unknown Person", candidates, threshold=0.9)
        (None, 0.25)
    """
    if not target_name or not candidate_names:
        return None, 0.0
    
    normalized_target = normalize_name(target_name)
    
    best_match = None
    best_score = 0.0
    
    for candidate_name in candidate_names:
        normalized_candidate = normalize_name(candidate_name)
        
        # Calculate similarity ratio
        similarity = SequenceMatcher(None, normalized_target, normalized_candidate).ratio()
        
        if similarity > best_score:
            best_score = similarity
            best_match = candidate_name
    
    # Only return match if above threshold
    if best_score >= threshold:
        return best_match, best_score
    else:
        return None, best_score


def match_and_save_partners(kyc_partners, edd_partners, threshold=0.8, 
                            output_path="partner_name_mapping.json", verbose=True):
    """
    Match KYC partners with EDD partners and save the mapping.
    
    Args:
        kyc_partners (list): List of dicts with 'name' and 'folder_name' keys
        edd_partners (list): List of EDD partner names (strings)
        threshold (float): Similarity threshold for matching
        output_path (str): Path to save the mapping
        verbose (bool): Print matching details
        
    Returns:
        list: List of match results with all details
    """
    matches = []
    
    if verbose:
        print(f"\n{'='*80}")
        print("PARTNER NAME MATCHING")
        print(f"{'='*80}\n")
    
    for kyc_partner in kyc_partners:
        kyc_name = kyc_partner["name"]
        folder_name = kyc_partner.get("folder_name", "unknown")
        
        if verbose:
            print(f"KYC Partner: {kyc_name}")
            print(f"  Folder: {folder_name}")
            print(f"  Normalized: {normalize_name(kyc_name)}")
        
        # Use fuzzy_match_name function here
        matched_name, score = fuzzy_match_name(kyc_name, edd_partners, threshold)
        
        match_record = {
            "kyc_partner_name": kyc_name,
            "kyc_folder_name": folder_name,
            "kyc_normalized": normalize_name(kyc_name),
            "matched_edd_name": matched_name,
            "edd_normalized": normalize_name(matched_name) if matched_name else None,
            "similarity_score": round(score, 4),
            "match_status": "matched" if matched_name else "unmatched",
            "timestamp": datetime.now().isoformat()
        }
        
        matches.append(match_record)
        
        if verbose:
            if matched_name:
                print(f"  ✓ MATCHED with: {matched_name}")
                print(f"    EDD Normalized: {normalize_name(matched_name)}")
                print(f"    Similarity: {score:.2%}")
            else:
                print(f"  ✗ NO MATCH (best score: {score:.2%})")
            print(f"{'-'*80}\n")
    
    # Save to file
    mapping_data = {
        "created_at": datetime.now().isoformat(),
        "threshold_used": threshold,
        "mappings": matches,
        "stats": {
            "total_kyc_partners": len(matches),
            "matched_partners": len([m for m in matches if m["matched_edd_name"]]),
            "unmatched_partners": len([m for m in matches if not m["matched_edd_name"]]),
            "match_rate": len([m for m in matches if m["matched_edd_name"]]) / len(matches) if matches else 0
        }
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapping_data, f, indent=2, ensure_ascii=False)
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"✓ Saved mapping to: {output_path}")
        print(f"Stats: {mapping_data['stats']['matched_partners']}/{mapping_data['stats']['total_kyc_partners']} matched ({mapping_data['stats']['match_rate']:.1%})")
        print(f"{'='*80}\n")
    
    return matches


def load_partner_mapping(mapping_path="partner_name_mapping.json"):
    """
    Load partner name mapping from JSON file.
    
    Args:
        mapping_path (str): Path to the mapping JSON file
    
    Returns:
        dict: Simple mapping of KYC names to EDD names
    """
    with open(mapping_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Convert to simple dict for easy lookup
    mapping = {}
    for match in data["mappings"]:
        if match["matched_edd_name"]:
            mapping[match["kyc_partner_name"]] = match["matched_edd_name"]
    
    return mapping


def get_edd_partner_name(kyc_name, mapping_path="partner_name_mapping.json"):
    """
    Get the EDD partner name for a given KYC partner name.
    
    Args:
        kyc_name (str): KYC partner name
        mapping_path (str): Path to mapping file
        
    Returns:
        str or None: Matched EDD partner name, or None if not found
    """
    mapping = load_partner_mapping(mapping_path)
    return mapping.get(kyc_name)
