from main.riskflag_detection.scap_tree import SCAPGraph

def run_section_scap_flag_checks(
    partner_info,
    partner_name: str,
    folder_name: str,
    kyc_checks_output: dict,
    output_folder: str,
    edd_parsed: dict,
) -> None:
    logger.info("========== START SECTION 13: SCAP flag checks ==========")

    client_notes = partner_info.kyc_dataset.get("total_assets", {}).get("remarks_total_assets", "")
    dict_activities = partner_info.incomes_dict

    scap_state = SCAPGraph().invoke(client_notes, dict_activities)

    scap1_flag = scap_state.get("scap1_flag", "Missing Information")
    scap2_flag = scap_state.get("scap2_flag", "Missing Information")

    risk_categories = edd_parsed.get("risk_category", [])
    flags = kyc_checks_output["scap_flags"]

    # Update output with results
    flags["reason"] += f"\n**{partner_name}**\nSCAP1 Flag: {scap1_flag}\nSCAP2 Flag: {scap2_flag}\n"

    # Check discrepancies between SCAP flags and EDD risk categories
    discrepancies = [
        ("SCAP", "SCAP-1", scap1_flag, "SCAP1 identified, but SCAP-1 is not reported in EDD risk category.\n"),
        ("SCAP", "SCAP-2", scap2_flag, "SCAP2 identified, but SCAP-2 is not reported in EDD risk category.\n"),
    ]
    for scap_key, edd_key, flag, message in discrepancies:
        if scap_key in flag and edd_key not in risk_categories:
            flags["status"] = False
            flags["reason"] += message

    # Handle missing information
    if "Missing Information" in (scap1_flag, scap2_flag):
        flags["status"] = False
        flags["reason"] += "We are missing information about wealth-creating activity to deduce SCAP relevance.\n"

    # No SCAP flags detected
    elif "SCAP" not in scap1_flag and "SCAP" not in scap2_flag:
        flags["reason"] += "No SCAP flags detected.\n"

    logger.info("========== END SECTION 13: SCAP flag checks ==========")
