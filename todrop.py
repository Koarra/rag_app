import json
import pandas as pd
import os
from coreruler.data_abstractions.query import Query
from neuralkyc.data.datasets.legal_entity import LegalEntity
from neuralkyc.app_report.kyc_data_handler import KYCDataHandler
from utils.prompts import ORIGIN_OF_ASSET_PROMPT
from utils.func_utils import get_llm
from constants import OU_CODE_DATA_PATH, ORIGIN_OF_ASSET_ARGS
from utils.name_matching import match_and_save_partners, load_partner_mapping, get_edd_partner_name


class KycChecksOutput:
    
    @staticmethod
    def processing(client_histories_parsed, edd_parsed, edd_txt_dic):
        
        # Get all partner names from EDD total_wealth_composition
        total_wealth_comp_list = edd_parsed.get("total_wealth_composition", [])
        edd_partner_names = [partner["name"] for partner in total_wealth_comp_list]
        
        print(f"\nEDD Partners found: {edd_partner_names}")
        print(f"{'='*80}\n")
        
        # ===== PARTNER NAME MATCHING AND SAVING =====
        # Prepare KYC partner data
        kyc_partners = []
        for partner_info in client_histories_parsed:
            folder_name = os.path.basename(partner_info.kyc_folder_path)
            kyc_partner_name = partner_info.kyc_dataset.name
            kyc_partners.append({
                "name": kyc_partner_name,
                "folder_name": folder_name
            })
        
        # Match and save to JSON file
        matches = match_and_save_partners(
            kyc_partners, 
            edd_partner_names,
            threshold=0.8,
            output_path="/mnt/user-data/outputs/partner_name_mapping.json",
            verbose=True
        )
        
        # Apply the matches to edd_parsed for downstream processing
        for match in matches:
            matched_edd_name = match["matched_edd_name"]
            
            if matched_edd_name:
                # Add to EDD data
                for partner_dict in edd_parsed["total_wealth_composition"]:
                    if partner_dict["name"] == matched_edd_name:
                        partner_dict["kyc_folder_name"] = match["kyc_folder_name"]
                        partner_dict["kyc_partner_name"] = match["kyc_partner_name"]
                        partner_dict["similarity_score"] = match["similarity_score"]
                        break
        
        print(f"Partner name matching completed and saved!")
        print(f"{'='*80}\n")
        
        # ===== NOW START THE MAIN PROCESSING LOOP =====
        # load EDD br text parsed to get the BU extracted and type of BU
        edd_req_type = edd_parsed["request_type"]
        edd_ou = edd_parsed["org_unit"]
        ou_df = pd.read_csv(OU_CODE_DATA_PATH)
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
        
        # Now process each KYC partner
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
            for edd_partner in edd_parsed.get("total_wealth_composition", []):
                if edd_partner.get("kyc_folder_name") == folder_name:
                    matched_edd_partner = edd_partner
                    print(f"✓ This partner matches EDD partner: {edd_partner['name']}")
                    print(f"  Similarity score: {edd_partner.get('similarity_score', 'N/A')}")
                    break
            
            if not matched_edd_partner:
                print(f"⚠ Warning: No EDD partner match found for {kyc_partner_name}")
            
            print("Available attributes:", dir(partner_info.kyc_dataset))
            print("Instance type:", type(partner_info.kyc_dataset))
            print(f"Is it a legal entity ?/", isinstance(partner_info.kyc_dataset, LegalEntity))
            
            # ... rest of your existing KYC checks code
            # Continue with your origin of assets checks, activity checks, etc.
        
        return kyc_checks_output
