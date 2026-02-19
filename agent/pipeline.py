"""
pipeline.py
Main KYC checks pipeline — entry point.

Usage:
    from kyc_agent.pipeline import run_kyc_checks_pipeline
    results = run_kyc_checks_pipeline(...)
"""

import os
from glob import glob

from kyc_agent.utils import (
    build_llm,
    load_edd_case,
    resolve_ou_mapping,
    resolve_partner_info,
    serialise_kyc_dataset,
)
from kyc_agent.checks import run_section3, run_section4

KYC_CHECK_KEYS = [
    "sign_off", "additional_sign_offs", "purpose_of_business_relationships",
    "origin_of_asset", "corroboration", "percentage_total_assets_explained",
    "remarks_on_total_assets_and_composition", "activity", "transactions",
    "family_situation", "consistency_checks_within_kyc",
    "consistency_checks_within_kyc_contradiction_checks",
    "consistency_checks_with_previous_edd", "scap_flags", "siap_flags",
]

OUT_OF_SCOPE_CHECKS = [
    "sign_off", "additional_sign_offs", "corroboration",
    "transactions", "consistency_checks_within_kyc",
    "consistency_checks_with_previous_edd",
]


def run_kyc_checks_pipeline(
    input_folder: str,
    output_folder: str,
    ou_code_data_path: str,
    edd_name: str,
    case_number: str,
    kyc_to_edd_partner_matches: dict,
    client_histories_parsed: list,
    edd_text_parser,
) -> dict:
    """
    Run the full KYC checks pipeline.
    Returns kyc_checks_output dict with status and reason for each check section.
    """
    # Initialise output structure
    kyc_checks_output = {}
    dict_kyc_checks_name_display = {
        "sign_off": "1. Sign-Off",
        "additional_sign_offs": "2. Additional Sign-Offs",
        "purpose_of_business_relationships": "3. Purpose of Business Relationship",
        "origin_of_asset": "4. Origin of Assets",
        "corroboration": "5. Corroboration and Evidence",
        "percentage_total_assets_explained": "6. Total Assets / Composition of Assets",
        "remarks_on_total_assets_and_composition": "7. Remarks on Total Assets and Asset Composition",
        "activity": "8. Activity",
        "transactions": "9. Transactions",
        "family_situation": "10. Family Situation",
        "consistency_checks_within_kyc": "11.1 Consistency Checks within the KYC - role holders and ASM numbers",
        "consistency_checks_within_kyc_contradiction_checks": "11.2 Consistency Checks within the KYC - contradiction checks: one field vs other fields",
        "consistency_checks_with_previous_edd": "12. Consistency Checks with Previous EDD Assessment",
        "scap_flags": "13. SCAP Flags",
        "siap_flags": "14. SIAP Flags",
    }
    for check_name, display_name in dict_kyc_checks_name_display.items():
        kyc_checks_output[check_name] = {}
        kyc_checks_output[check_name]["status"] = True
        kyc_checks_output[check_name]["reason"] = ""
        kyc_checks_output[check_name]["display_name"] = display_name
        if check_name in OUT_OF_SCOPE_CHECKS:
            kyc_checks_output[check_name]["reason"] = "Out of scope currently."

    # Load EDD
    edd_case = load_edd_case(input_folder, edd_text_parser)
    print("TOTAL WEALTH:", edd_case.get("total_wealth_composition", []))
    ou_code_mapped = resolve_ou_mapping(edd_case, ou_code_data_path)

    # Resolve partner
    kyc_folder, partner_info = resolve_partner_info(
        kyc_to_edd_partner_matches, client_histories_parsed, edd_name
    )
    if kyc_folder is None or partner_info is None:
        print("Could not resolve partner info. Aborting pipeline.")
        return kyc_checks_output

    folder_name = os.path.join(case_number, os.path.basename(partner_info.kyc_folder_path))
    partner_name = partner_info.partner_name
    llm = build_llm()

    serialise_kyc_dataset(partner_info, output_folder, folder_name)

    # Run checks
    run_section3(
        partner_info=partner_info, partner_name=partner_name, folder_name=folder_name,
        ou_code_mapped=ou_code_mapped, kyc_checks_output=kyc_checks_output,
        output_folder=output_folder, llm=llm,
    )
    run_section4(
        partner_info=partner_info, partner_name=partner_name, folder_name=folder_name,
        kyc_checks_output=kyc_checks_output, output_folder=output_folder, llm=llm,
    )
    # run_section6(...)  # add as more sections arrive

    return kyc_checks_output


if __name__ == "__main__":
    # --- Configuration ---
    INPUT_FOLDER = "data/input"
    OUTPUT_FOLDER = "data/output"
    OU_CODE_DATA_PATH = "data/ou_codes.csv"

    # --- Load and parse EDD case ---
    edd_case = load_edd_case(INPUT_FOLDER, edd_text_parser)

    # --- edd_name comes from contractual partner information ---
    edd_name = edd_case["contractual_partner_information"]["name"]

    # --- edd_partner_names from total_wealth_composition ---
    edd_partner_names = [
        partner["name"]
        for partner in edd_case.get("total_wealth_composition", [])
    ]

    # --- Get partner folders and derive case_number from folder path ---
    edd_case_path_folder = glob(INPUT_FOLDER + "/DD-**")[2]
    partner_folders = glob(edd_case_path_folder + "/Partners/*")
    case_number = edd_case_path_folder.split("/")[-1]

    print("2", case_number)
    print("3", partner_folders)

    # --- Process KYC PDFs ---
    kyc_cases = [
        process_kyc_pdf(partner_folder)
        for partner_folder in partner_folders
    ]

    print("STEPXx")
    print("1", kyc_cases)
    print("x", edd_case_path_folder)

    # --- Match KYC partners to EDD partners via fuzzy matching ---
    kyc_to_edd_partner_matches = match_and_save_partners(
        kyc_cases,
        edd_partner_names,
        threshold=0.8,
        output_path=OUTPUT_FOLDER + "/" + case_number + "/partner_name_mapping.json",
        verbose=True,
    )

    print("STEP###")

    # --- Remove empty KYC datasets (e.g. PDFs not properly processed) ---
    client_histories_parsed = [
        item for item in kyc_cases if item.kyc_dataset is not None
    ]

    print("client_history_parsed", client_histories_parsed)
    print(f"Available attributes: {dir(client_histories_parsed)}")
    print("kyc_dataset keys:", client_histories_parsed[0].kyc_dataset.keys())

    iteration = 0

    # --- Run pipeline once per EDD partner ---
    for edd_name in edd_partner_names:
        print(f"\nRunning pipeline for: {edd_name}")
        results = run_kyc_checks_pipeline(
            input_folder=INPUT_FOLDER,
            output_folder=OUTPUT_FOLDER,
            ou_code_data_path=OU_CODE_DATA_PATH,
            edd_name=edd_name,
            case_number=case_number,
            kyc_to_edd_partner_matches=kyc_to_edd_partner_matches,
            client_histories_parsed=client_histories_parsed,
            edd_text_parser=edd_text_parser,
        )
        print(f"Done: {edd_name}")
        print(results)