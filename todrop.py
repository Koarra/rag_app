# Add this to kyc_checks_output.py

from utils.func_utils import get_llm
from coreruler.data_abstractions.query import Query

# Add these constants (or put them in your constants.py file)
PARTNER_NAME_MATCHING_PROMPT = """You are helping match partner names from different data sources.

KYC Partner Name: {kyc_partner_name}

EDD Partner Names (from text file):
{edd_partner_list}

Task: Which EDD partner name most likely refers to the same person/entity as the KYC partner name?

Return ONLY the matching EDD partner name exactly as it appears in the list, or "NO_MATCH" if none match.
Do not include any explanation."""

PARTNER_NAME_MATCHING_ARGS = {
    "model": "claude-sonnet-4-5-20250929",
    "size": "4k",
    "llama_cpp_kwargs": {
        "grammar": None,  # No grammar needed for this task
        "seed": 420,
        "temperature": 0.0,
    },
}

def match_partner_name(kyc_partner_name, edd_partner_names):
    """
    Use LLM to match a KYC partner name with the most likely EDD partner name
    """
    llm_partner_matcher = get_llm(PARTNER_NAME_MATCHING_ARGS)
    
    # Format the EDD partner names as a bulleted list
    edd_partner_list = "\n".join(f"- {name}" for name in edd_partner_names)
    
    query = Query(
        query_setup=PARTNER_NAME_MATCHING_PROMPT,
        model=llm_partner_matcher,
        system_prompt="You are a name matching assistant. Match names accurately based on context and variations."
    )
    
    result = query.invoke({
        "kyc_partner_name": kyc_partner_name,
        "edd_partner_list": edd_partner_list
    })
    
    matched_name = result.strip()
    
    # Return None if no match found
    if matched_name == "NO_MATCH" or matched_name not in edd_partner_names:
        return None
    
    return matched_name


# Then modify your processing function:
@staticmethod
def processing(client_histories_parsed, edd_parsed, edd_txt_dic):
    import os
    
    # Get all partner names from EDD total_wealth_composition
    edd_partner_names = list(edd_txt_dic.get("total_wealth_composition", {}).keys())
    
    print(f"\nEDD Partners found in text file: {edd_partner_names}")
    print(f"{'='*80}\n")
    
    # Match each KYC partner with EDD partners
    for partner_info in client_histories_parsed:
        folder_name = os.path.basename(partner_info.kyc_folder_path)
        kyc_partner_name = partner_info.kyc_dataset.name
        
        print(f"Processing KYC folder: {folder_name}")
        print(f"KYC Partner Name: {kyc_partner_name}")
        
        # Use LLM to match with EDD partner
        matched_edd_name = match_partner_name(kyc_partner_name, edd_partner_names)
        
        if matched_edd_name:
            print(f"✓ Matched with EDD partner: {matched_edd_name}")
            
            # Add folder name to the matched EDD partner's data
            edd_txt_dic["total_wealth_composition"][matched_edd_name]["kyc_folder_name"] = folder_name
            edd_txt_dic["total_wealth_composition"][matched_edd_name]["kyc_partner_name"] = kyc_partner_name
        else:
            print(f"✗ No match found for KYC partner: {kyc_partner_name}")
        
        print(f"{'-'*80}\n")
    
    # Continue with your existing processing code
    # ... rest of your code
