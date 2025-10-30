@staticmethod
def processing(client_histories_parsed, edd_parsed, edd_txt_dic):
    
    # Get all partner names from EDD total_wealth_composition (it's a list)
    total_wealth_comp_list = edd_parsed.get("total_wealth_composition", [])
    
    # Extract just the partner names from the list
    edd_partner_names = [partner["name"] for partner in total_wealth_comp_list]
    
    print(f"\nEDD Partners found in text file: {edd_partner_names}")
    print(f"{'='*80}\n")
    
    # ===== PARTNER NAME MATCHING SECTION (BEFORE PROCESSING) =====
    print("Starting partner name matching...")
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
    
    # Match each KYC partner with EDD partners
    for kyc_data in kyc_partner_names:
        folder_name = kyc_data["folder_name"]
        kyc_partner_name = kyc_data["partner_name"]
        
        print(f"Matching KYC folder: {folder_name}")
        print(f"KYC Partner Name: {kyc_partner_name}")
        
        # Use LLM to match with EDD partner
        matched_edd_name = match_partner_name(kyc_partner_name, edd_partner_names)
        
        if matched_edd_name:
            print(f"✓ Matched with EDD partner: {matched_edd_name}")
            
            # Find the partner in the list and add the folder info
            for partner_dict in edd_parsed["total_wealth_composition"]:
                if partner_dict["name"] == matched_edd_name:
                    partner_dict["kyc_folder_name"] = folder_name
                    partner_dict["kyc_partner_name"] = kyc_partner_name
                    break
        else:
            print(f"✗ No match found for KYC partner: {kyc_partner_name}")
        
        print(f"{'-'*80}\n")
    
    print("Partner name matching completed!")
    print(f"{'='*80}\n")
    
    # ===== NOW START THE MAIN PROCESSING LOOP =====
    # At this point, each partner dict in edd_parsed["total_wealth_composition"] 
    # has been enriched with kyc_folder_name and kyc_partner_name (if matched)
    
    # load EDD br text parsed to get the BU extracted and type of BU
    edd_req_type = edd_parsed["request_type"]
    edd_ou = edd_parsed["org_unit"]
    
    # ... rest of your existing code
    
    # Later in your loop, you can find matched partners like this:
    for partner_info in client_histories_parsed:
        folder_name = os.path.basename(partner_info.kyc_folder_path)
        kyc_partner_name = partner_info.kyc_dataset.name
        
        print(f"\n{'='*60}")
        print(f"Running KYC analysis for folder: {folder_name}")
        print(f"KYC Partner Name: {kyc_partner_name}")
        print(f"{'='*60}\n")
        
        # Find the corresponding EDD partner
        matched_edd_partner = None
        for edd_partner in edd_parsed["total_wealth_composition"]:
            if edd_partner.get("kyc_folder_name") == folder_name:
                matched_edd_partner = edd_partner
                print(f"This partner matches EDD partner: {edd_partner['name']}")
                break
        
        if not matched_edd_partner:
            print(f"⚠ Warning: No EDD partner match found for {kyc_partner_name}")
        
        # Continue with your existing KYC checks...
