# ============================================
# Section 11.2: Consistency Checks within the KYC: contradictory information check 1 vs rest
# ============================================
logger.info("START SECTION 11.2: Consistency checks within the KYC: contradictory information checks")
results_contradiction = {}

logger.info(f"Starting contradiction checks for partner: {partner_name}")
logger.info(f"Number of fields to check: {len(kyc_dict)}")

for field_name, field_value in kyc_dict.items():
    logger.info(f"Running contradiction check for field: {field_name}")
    other_fields = {k: v for k, v in kyc_dict.items() if k != field_name}
    # TODO HERE
    response_llm_contradiction_checks = contradiction_checks(
        field_value, other_fields
    )
    logger.info(f"Contradiction check result for {field_name}: {response_llm_contradiction_checks}")
    results_contradiction[f"{field_name}_vs_rest"] = (
        response_llm_contradiction_checks
    )

is_contradiction = any(
    result["contradictory"].lower() == "true"
    and result["confidence_level"] > 0.8
    for result in results_contradiction.values()
)
logger.info(f"Overall contradiction detected: {is_contradiction}")

kyc_checks_output["consistency_checks_within_kyc_contradiction_checks"][
    "status"
] &= not is_contradiction
kyc_checks_output["consistency_checks_within_kyc_contradiction_checks"][
    "reason"
] += f"\n\n**{partner_name}***"
kyc_checks_output["consistency_checks_within_kyc_contradiction_checks"][
    "reason"
] += "\n**KYC contradiction check**:"

for field_name, result in results_contradiction.items():
    logger.info(
        f"Field: {field_name} | Contradictory: {result['contradictory']} | "
        f"Confidence: {result['confidence_level']:.2%} | Reasoning: {result['reasoning']}"
    )
    kyc_checks_output["consistency_checks_within_kyc_contradiction_checks"][
        "reason"
    ] += (
        f"\n\n{field_name.replace('_', ' ').capitalize()}** - "
        + (
            "contradictions present.\n"
            if result["contradictory"].lower() == "true"
            else "no contradictions identified.\n"
        )
        + f"**Confidence level**: {result['confidence_level']:.2%}\n"
        + f"**Reasoning**: {result['reasoning']}\n"
    )

save_json(
    results_contradiction,
    output_folder,
    folder_name,
    "section11_2_kyc_data_check_kyc_contradiction.json",
)
logger.info("Intermediate data saved: kyc contradiction checks")

# ============================================
# Section 13: SCAP flag checks
# ============================================
logger.info("START SECTION 13: SCAP flag checks")
logger.info(f"Processing SCAP flags for partner: {partner_name}")

risk_flags_and_corrob = KYCDataHandler("", [], partner_info.kyc_dataset)
logger.info(f"SCAP 1 result: {risk_flags_and_corrob.result_scap1_short}")
logger.info(f"SCAP 2 result: {risk_flags_and_corrob.result_scap2_short}")

kyc_checks_output["scap_flags"]["reason"] += f"\n\n**{partner_name}**\n"
scap_results = {
    "SCAP 1": str(risk_flags_and_corrob.result_scap1_short),
    "SCAP 2": str(risk_flags_and_corrob.result_scap2_short),
}

for scap_key, scap_value in scap_results.items():
    logger.info(f"Evaluating {scap_key}: {scap_value}")
    if scap_key in scap_value:
        # Check if SCAP reported in EDD and flag if not
        if (
            scap_key == "SCAP 1"
            and "SCAP-1" not in edd_parsed.get("risk_category", [])
        ):
            logger.info(f"{scap_key} found in KYC but not in EDD risk_category - flagging red")
            kyc_checks_output["scap_flags"]["status"] = False
        if (
            scap_key == "SCAP 2"
            and "SCAP-2" not in edd_parsed.get("risk_category", [])
        ):
            logger.info(f"{scap_key} found in KYC but not in EDD risk_category - flagging red")
            kyc_checks_output["scap_flags"]["status"] = False
            kyc_checks_output["scap_flags"]["reason"] += f"{scap_value}\n"
    if "Missing information" in scap_value:
        logger.info(f"{scap_key} has missing information - flagging red")
        kyc_checks_output["scap_flags"]["status"] = False
        kyc_checks_output["scap_flags"][
            "reason"
        ] += f"We are missing information about wealth creating activity to deduce {scap_key} relevance.\n"

if (
    "SCAP1" not in scap_results["SCAP 1"]
    and "SCAP2" not in scap_results["SCAP 2"]
):
    logger.info("No SCAP flags detected")
    kyc_checks_output["scap_flags"]["reason"] += "No SCAP flags detected.\n"

logger.info(f"SCAP flags final status: {kyc_checks_output['scap_flags']['status']}")

# ============================================
# Section 14: SIAP flag checks
# ============================================
logger.info("START SECTION 14: SIAP flag checks")
logger.info(f"Processing SIAP flags for partner: {partner_name}")

kyc_checks_output["siap_flags"]["reason"] += f"\n\n**{partner_name}**\n"
logger.info(f"SIAP results table shape: {risk_flags_and_corrob.siap_results_table.shape}")

siap_items = risk_flags_and_corrob.siap_results_table[
    risk_flags_and_corrob.siap_results_table.iloc[:, 1]
    .astype(str)
    .str.contains(
        "Missing Information Node|SIAP EDD|Prohibited Relation", regex=True
    )
]
logger.info(f"SIAP items requiring attention: {len(siap_items)}")

if not siap_items.empty:
    logger.info("SIAP items found - checking against EDD risk category")
    kyc_checks_output["siap_flags"][
        "reason"
    ] += "There are SIAP items needing attention.\n"
    # Only flag red in case EDD does not have the SIAP flag already
    if "SIAP" not in edd_parsed.get("risk_category", []):
        logger.info("SIAP not in EDD risk_category - flagging red")
        kyc_checks_output["siap_flags"]["status"] = False
    else:
        logger.info("SIAP already present in EDD risk_category - not flagging red")
else:
    logger.info("No SIAP items requiring attention detected")
    kyc_checks_output["siap_flags"][
        "reason"
    ] += "No SIAP activities detected.\n"

tmp_title = "\n**LLM Processing Trace:**"
tmp = ""
col_names = ["Eligible SIAP Tree", "Findings"]
for tree, findings in zip(
    *[risk_flags_and_corrob.siap_results_table[x] for x in col_names]
):
    logger.info(f"Processing SIAP tree: {tree}")
    tmp += f"\n**Eligible SIAP Category**: {tree}"
    findings = (
        findings.replace("**: :", ": :")
        .replace("***", "\n- ")
        .replace("Missing Information Node", "Missing Information")
        .replace("NOT SIAP", "Not SIAP")
    )
    tmp += f"\n**Findings**: {findings}\n"

kyc_checks_output["siap_flags"]["reason"] += tmp_title + (
    tmp if len(tmp) > 0 else "\nN/A (no eligible SIAP trees were identified).\n"
)
logger.info(f"SIAP flags final status: {kyc_checks_output['siap_flags']['status']}")

# ============================================
# Section 11.1: Consistency Checks within the KYC
# ============================================
logger.info("START SECTION 11.1: Consistency checks within the KYC")
# Role Holders sufficiency check
quality_check_role_holders = "N/A (no DomCo, OpCo, trust, or foundation)."
logger.info(f"Checking role holders for partner: {partner_name}")

business_relationship_type = edd_parsed.get(
    "type_of_business_relationship", {}
).get("_type", "")
logger.info(f"Business relationship type: {business_relationship_type}")

# DomCo
if "Domiciliary Company" in business_relationship_type:
    logger.info("DomCo detected - checking role holders")
    if (
        edd_parsed.get("poa_list") is not None
        and len(edd_parsed.get("role_holders_information", [])) > 1
    ):
        quality_check_role_holders = "contains at least one BO and one PoA."
        logger.info("DomCo role holders check passed")
    else:
        quality_check_role_holders = (
            " missing information about at least one BO and one PoA."
        )
        logger.info("DomCo role holders check failed - flagging red")
        kyc_checks_output["consistency_checks_within_kyc"]["status"] = False

# Trust
if "Trust" in business_relationship_type:
    logger.info("Trust detected - checking role holders")
    if edd_parsed.get("poa_list") is not None and (
        role in edd_parsed.get("type_of_business_relationship", {})
        for role in ["trustee", "settlor", "beneficiary"]
    ):
        quality_check_role_holders = (
            "contains at least one trustee, settlor, beneficiary and one PoA."
        )
        logger.info("Trust role holders check passed")
    else:
        quality_check_role_holders = " missing information about at least one trustee, settlor, beneficiary and one PoA."
        logger.info("Trust role holders check failed - flagging red")
        kyc_checks_output["consistency_checks_within_kyc"]["status"] = False

# Foundation
if "Foundation" in business_relationship_type:
    logger.info("Foundation detected - checking role holders")
    if edd_parsed.get("poa_list") is not None and (
        role in edd_parsed.get("type_of_business_relationship", {})
        for role in ["founder", "beneficiary"]
    ):
        quality_check_role_holders = (
            "contains at least one founder, beneficiary and one PoA."
        )
        logger.info("Foundation role holders check passed")
    else:
        quality_check_role_holders = " missing information about at least one founder, beneficiary and one PoA."
        logger.info("Foundation role holders check failed - flagging red")
        kyc_checks_output["consistency_checks_within_kyc"]["status"] = False

# OpCo
if "Operating Company" in business_relationship_type:
    logger.info("OpCo detected - checking role holders")
    if edd_parsed.get("poa_list") is not None and (
        "controlling person" in edd_parsed.get("type_of_business_relationship", {})
    ):
        quality_check_role_holders = (
            "contains at least one controlling person and one PoA."
        )
        logger.info("OpCo role holders check passed")
    else:
        quality_check_role_holders = " missing information about at least one controlling person and one PoA."
        logger.info("OpCo role holders check failed - flagging red")
        kyc_checks_output["consistency_checks_within_kyc"]["status"] = False

# PEP Quality Check
logger.info("Running PEP quality check")
quality_check_pep = "N/A (no PEP mention, no sensitivity documents attached)."
if "PEP" in edd_parsed.get("risk_category", []) or pep_sensitivity_present:
    logger.info("PEP detected - checking ASM number")
    if "ASM" in edd_parsed.get("risk_category", []):
        quality_check_pep = "PEP ASM number documented."
        logger.info("ASM number found for PEP")
    else:
        quality_check_pep = "PEP ASM number not documented."
        logger.info("ASM number missing for PEP")

kyc_checks_output["consistency_checks_within_kyc"][
    "reason"
] += f"\n**Role holders sufficiency check**: {quality_check_role_holders}"
kyc_checks_output["consistency_checks_within_kyc"][
    "reason"
] += f"\n\n**ASM Number presence check**: {quality_check_pep}"

logger.info(
    f"Section 11.1 final status: {kyc_checks_output['consistency_checks_within_kyc']['status']}"
)

kyc_checks_output["raw_data"] = raw_data
logger.info("KYC checks processing complete - returning results")
return kyc_checks_output, kyc_to_edd_partner_matches