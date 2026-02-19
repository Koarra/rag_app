"""
pipeline.py
Main KYC checks pipeline — entry point.

Usage:
    from kyc_agent.pipeline import run_kyc_checks_pipeline
    results = run_kyc_checks_pipeline(...)
"""

import os

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
    kyc_checks_output = {key: {"status": True, "reason": ""} for key in KYC_CHECK_KEYS}

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
    results = run_kyc_checks_pipeline(
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        ou_code_data_path=OU_CODE_DATA_PATH,
        edd_name=EDD_NAME,
        case_number=CASE_NUMBER,
        kyc_to_edd_partner_matches=kyc_to_edd_partner_matches,
        client_histories_parsed=client_histories_parsed,
        edd_text_parser=edd_text_parser,
    )
    print("Pipeline complete.")
    print(results)
