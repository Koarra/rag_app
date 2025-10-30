@staticmethod
def processing(client_histories_parsed, edd_parsed, edd_txt_dic):
    
    # Get all partner names from EDD total_wealth_composition
    edd_partner_names = list(edd_txt_dic.get("total_wealth_composition", {}).keys())
    
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
            
            # Add folder name and KYC name to the matched EDD partner's data
            edd_txt_dic["total_wealth_composition"][matched_edd_name]["kyc_folder_name"] = folder_name
            edd_txt_dic["total_wealth_composition"][matched_edd_name]["kyc_partner_name"] = kyc_partner_name
        else:
            print(f"✗ No match found for KYC partner: {kyc_partner_name}")
        
        print(f"{'-'*80}\n")
    
    print("Partner name matching completed!")
    print(f"{'='*80}\n")
    
    # ===== NOW START THE MAIN PROCESSING LOOP =====
    # At this point, edd_txt_dic has been enriched with kyc_folder_name and kyc_partner_name
    
    # load EDD br text parsed to get the BU extracted and type of BU
    edd_req_type = edd_parsed["request_type"]
    edd_ou = edd_parsed["org_unit"]
    ou_df = pd.read_csv(OU_CODE_DATA_PATH) # to map to OU name
    ou_df = ou_df[["orgUnitCode", "managingOrgUnitName"]]
    edd_ou_name = ou_df[ou_df["orgUnitCode"] == edd_ou]["managingOrgUnitName"].values[0]
    
    # Initiate the output dictionary for storing results
    kyc_checks_output = {}
    kyc_checks_output["origin_of_asset"] = {}
    kyc_checks_output["origin_of_asset"]["status"] = True
    kyc_checks_output["origin_of_asset"]["reason"] = ''
    kyc_checks_output["activity"] = {}
    kyc_checks_output["activity"]["status"] = True
    kyc_checks_output["activity"]["reason"] = ''
    
    # Remove empty KYC datasets due to PDFs that were not properly processed
    print("start KYC CHECKS=============================================")
    client_histories_parsed = [item for item in client_histories_parsed if item.kyc_dataset is not None]
    
    # Now you can access the matched information in your loop
    for partner_info in client_histories_parsed:
        print("client history parsed", client_histories_parsed)
        print("PARTNER_INFO", partner_info)
        print("WHICH PARTNER :::", partner_info.kyc_dataset.name)
        
        folder_name = os.path.basename(partner_info.kyc_folder_path)
        kyc_partner_name = partner_info.kyc_dataset.name
        
        print(f"\n{'='*60}")
        print(f"Running KYC analysis for folder: {folder_name}")
        print(f"KYC Partner Name: {kyc_partner_name}")
        print(f"{'='*60}\n")
        
        # Find if this partner was matched with an EDD partner
        matched_edd_partner = None
        for edd_name, edd_data in edd_txt_dic.get("total_wealth_composition", {}).items():
            if edd_data.get("kyc_folder_name") == folder_name:
                matched_edd_partner = edd_name
                print(f"This partner matches EDD partner: {edd_name}")
                break
        
        if not matched_edd_partner:
            print(f"⚠ Warning: No EDD partner match found for {kyc_partner_name}")
        
        # Continue with your existing KYC checks...
        # ... rest of your processing code
