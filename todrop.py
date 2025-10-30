# In kyc_checks_output.py

def match_partner_names_with_llm(kyc_partner_name, edd_partner_names_list):
    """
    Use LLM to match KYC partner name with the most likely EDD partner name
    """
    from anthropic import Anthropic
    
    client = Anthropic()
    
    prompt = f"""You are helping match partner names from different data sources.

KYC Partner Name: {kyc_partner_name}

EDD Partner Names (from text file):
{chr(10).join(f"- {name}" for name in edd_partner_names_list)}

Task: Which EDD partner name most likely refers to the same person/entity as the KYC partner name?

Return ONLY the matching EDD partner name exactly as it appears in the list, or "NO_MATCH" if none match.
Do not include any explanation."""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    
    match = response.content[0].text.strip()
    return match if match != "NO_MATCH" else None


# Then in your processing function:
def processing(client_histories_parsed, edd_parsed, edd_txt_dic):
    import os
    
    # Get all partner names from EDD total_wealth_composition
    edd_partner_names = list(edd_txt_dic.get("total_wealth_composition", {}).keys())
    
    # Create mapping using LLM
    partner_to_folder = {}
    
    for partner_info in client_histories_parsed:
        folder_name = os.path.basename(partner_info.kyc_folder_path)
        kyc_partner_name = partner_info.kyc_dataset.name
        
        print(f"Matching KYC partner: {kyc_partner_name}")
        
        # Use LLM to find matching EDD partner name
        matched_edd_name = match_partner_names_with_llm(kyc_partner_name, edd_partner_names)
        
        if matched_edd_name:
            print(f"  ✓ Matched with EDD partner: {matched_edd_name}")
            
            # Add folder name to the matched EDD partner's data
            edd_txt_dic["total_wealth_composition"][matched_edd_name]["kyc_folder_name"] = folder_name
            edd_txt_dic["total_wealth_composition"][matched_edd_name]["kyc_partner_name"] = kyc_partner_name
            
            partner_to_folder[matched_edd_name] = {
                "folder_name": folder_name,
                "kyc_name": kyc_partner_name
            }
        else:
            print(f"  ✗ No match found for {kyc_partner_name}")
    
    # Continue with rest of processing
    for partner_info in client_histories_parsed:
        # ... your existing code
