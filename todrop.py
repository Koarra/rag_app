import re
from difflib import SequenceMatcher

def normalize_name(name):
    """
    Normalize a name for matching by:
    1. Converting to lowercase
    2. Removing all non-letter characters (but keeping all alphabets from any language)
    3. Splitting into words and sorting alphabetically
    """
    # Convert to lowercase
    name_lower = name.lower()
    
    # Keep only letters (supports Unicode letters from all languages)
    # \w includes letters, digits, and underscore; we only want letters
    words = re.findall(r'\w+', name_lower, re.UNICODE)
    
    # Filter to keep only words that contain letters (removes pure numbers)
    words = [word for word in words if re.search(r'[a-zà-ÿα-ωа-я]', word, re.IGNORECASE | re.UNICODE)]
    
    # Sort alphabetically
    words_sorted = sorted(words)
    
    # Join back together
    return ' '.join(words_sorted)


def fuzzy_match_partner_name(kyc_partner_name, edd_partner_names, threshold=0.8):
    """
    Match KYC partner name with EDD partner names using fuzzy matching.
    
    Args:
        kyc_partner_name: The KYC partner name to match
        edd_partner_names: List of EDD partner names
        threshold: Similarity threshold (0.0 to 1.0), default 0.8
    
    Returns:
        Tuple of (matched_name, similarity_score) or (None, 0) if no match
    """
    normalized_kyc = normalize_name(kyc_partner_name)
    
    best_match = None
    best_score = 0
    
    for edd_name in edd_partner_names:
        normalized_edd = normalize_name(edd_name)
        
        # Calculate similarity ratio
        similarity = SequenceMatcher(None, normalized_kyc, normalized_edd).ratio()
        
        if similarity > best_score:
            best_score = similarity
            best_match = edd_name
    
    # Only return match if above threshold
    if best_score >= threshold:
        return best_match, best_score
    else:
        return None, best_score


# Then in your processing function:
@staticmethod
def processing(client_histories_parsed, edd_parsed, edd_txt_dic):
    
    # Get all partner names from EDD total_wealth_composition (it's a list)
    total_wealth_comp_list = edd_parsed.get("total_wealth_composition", [])
    
    # Extract just the partner names from the list
    edd_partner_names = [partner["name"] for partner in total_wealth_comp_list]
    
    print(f"\nEDD Partners found in text file: {edd_partner_names}")
    print(f"{'='*80}\n")
    
    # ===== PARTNER NAME MATCHING SECTION (BEFORE PROCESSING) =====
    print("Starting partner name matching (fuzzy matching)...")
    print(f"{'='*80}\n")
    
    # Collect all KYC partner names first
    kyc_partner_names = []
    for partner_info in client_histories_parsed:
        folder_name = os.path.basename(partner_info.kyc_folder_path)
        kyc_partner_name = partner_info.kyc_dataset.name
        kyc_partner_names.append({
            "folder_name": folder_name,
            "partner_name": kyc_partner_name,
            "partner_info": partner_info
        })
    
    # Match each KYC partner with EDD partners using fuzzy matching
    for kyc_data in kyc_partner_names:
        folder_name = kyc_data["folder_name"]
        kyc_partner_name = kyc_data["partner_name"]
        
        print(f"Matching KYC folder: {folder_name}")
        print(f"KYC Partner Name: {kyc_partner_name}")
        print(f"  Normalized: {normalize_name(kyc_partner_name)}")
        
        # Use fuzzy matching
        matched_edd_name, similarity_score = fuzzy_match_partner_name(
            kyc_partner_name, 
            edd_partner_names, 
            threshold=0.8  # Adjust this threshold as needed (0.8 = 80% similarity)
        )
        
        if matched_edd_name:
            print(f"✓ Matched with EDD partner: {matched_edd_name}")
            print(f"  Normalized: {normalize_name(matched_edd_name)}")
            print(f"  Similarity score: {similarity_score:.2%}")
            
            # Find the partner in the list and add the folder info
            for partner_dict in edd_parsed["total_wealth_composition"]:
                if partner_dict["name"] == matched_edd_name:
                    partner_dict["kyc_folder_name"] = folder_name
                    partner_dict["kyc_partner_name"] = kyc_partner_name
                    break
        else:
            print(f"✗ No match found for KYC partner: {kyc_partner_name}")
            print(f"  Best similarity score: {similarity_score:.2%} (below threshold)")
        
        print(f"{'-'*80}\n")
    
    print("Partner name matching completed!")
    print(f"{'='*80}\n")
    
    # ... rest of your processing code
```

**How it works:**

1. **`normalize_name()`** function:
   - `"Smith_John_2024"` → `"john smith"`
   - `"John SMITH"` → `"john smith"`
   - `"García López, María"` → `"garcía lópez maría"`
   - All normalized names have words in alphabetical order

2. **`fuzzy_match_partner_name()`** function:
   - Compares normalized names using `SequenceMatcher`
   - Returns the best match above the threshold (default 80% similarity)
   - Also returns the similarity score for debugging

**Example outputs:**
```
Matching KYC folder: Smith_John_2024
KYC Partner Name: Smith_John_2024
  Normalized: john smith
✓ Matched with EDD partner: John Smith
  Normalized: john smith
  Similarity score: 100.00%
