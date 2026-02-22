# ============================================
# Section 7: Remarks on total asset and asset composition
# ============================================
logger.info("START SECTION7: remarks on total assets and assets composition")
if partner_info.kyc_dataset["client_type"] == "Natural Person":
    logger.info("instance is individual")
    logger.info(
        f"KYC_TOTAL_ASSETS : {partner_info.kyc_dataset.get('total_assets', {}).get('total_assets')}"
    )
    logger.info(
        f"KYC_TOTAL_ASSETS remarks: {partner_info.kyc_dataset.get('total_assets', {}).get('description')}"
    )

    kyc_total_assets_str = (
        str(partner_info.kyc_dataset.get("total_assets", {}).get("total_assets"))
        if partner_info.kyc_dataset.get("total_assets", {}).get("total_assets")
        else "No kyc total assets text extracted"
    )
    kyc_total_remarks_str = (
        str(partner_info.kyc_dataset.get("total_assets", {}).get("description"))
        if partner_info.kyc_dataset.get("total_assets", {}).get("description")
        else "No kyc total assets remarks text extracted"
    )

    data_check_composition_of_ta = check_composition_of_total_assets(
        kyc_total_remarks_str
    )
    save_json(
        data_check_composition_of_ta,
        output_folder,
        folder_name,
        "section7_kyc_data_check_composition_of_total_assets.json",
    )
    logger.info("intermediate data saved: data check composition of total assets")

    data_kyc_remarks_comp_total_assets = compare_remarks_with_total_assets(
        kyc_total_remarks_str, kyc_total_assets_str
    )
    save_json(
        data_kyc_remarks_comp_total_assets,
        output_folder,
        folder_name,
        "section7_kyc_remarks_composition_total_assets.json",
    )
    logger.info(
        "Intermediate data saved: data kyc remarks composition of total assets"
    )

    remarks_sufficiency_checks = data_kyc_remarks_comp_total_assets[
        "sufficient_explanation"
    ]
    remarks_sufficiency_checks_reasoning = data_kyc_remarks_comp_total_assets[
        "reasoning"
    ]
    total_assets_remarks = data_check_composition_of_ta["total_assets_remarks"]

    if not kyc_total_assets or kyc_total_assets == 0:
        percentage_total_remarks_vs_total_assets = 0
        kyc_checks_output["remarks_on_total_assets_and_composition"][
            "status"
        ] = False
        kyc_checks_output["remarks_on_total_assets_and_composition"][
            "reason"
        ] += f"\n\n**{partner_name}** \nThe total assets denominator is null or zero, cannot calculate percentages.\n\n"
        logger.info("Cannot calculate percentages - denominator is null/zero")
    else:
        percentage_total_remarks_vs_total_assets = (
            total_assets_remarks / kyc_total_assets
        )
        percentage_validation = 0.8

        kyc_checks_output["remarks_on_total_assets_and_composition"][
            "reason"
        ] += f"\n\n**{partner_name}** \n**7.1**: The amount mentioned in the remarks on total assets is {total_assets_remarks :0,.2f}, representing **{percentage_total_remarks_vs_total_assets:.2%}** of the total assets indicated in the KYC ({kyc_total_assets :0,.2f})."
        followup = f"The remarks on total assets {'do not ' if not remarks_sufficiency_checks else ''}fully explain or support the total assets section."
        kyc_checks_output["remarks_on_total_assets_and_composition"][
            "reason"
        ] += f"\n\n**7.2**: {followup}\n"

        if percentage_total_remarks_vs_total_assets >= percentage_validation:
            logger.info(
                f"successfull check: percentage of specific asset fields composing to total assets >= 0.8: {percentage_of_specific_asset_fields_explaining_total_assets}"
            )
            logger.info(
                f"successfull check: percentage of total assets with known origin >= 0.8: {percentage_of_total_assets_with_known_origin}"
            )
        else:
            logger.info("Low percentage of total asset verification")
            kyc_checks_output["remarks_on_total_assets_and_composition"][
                "status"
            ] = False

        if not remarks_sufficiency_checks:
            kyc_checks_output["remarks_on_total_assets_and_composition"][
                "status"
            ] = False

        kyc_checks_output["remarks_on_total_assets_and_composition"][
            "reason"
        ] += f"**Reasoning**: {remarks_sufficiency_checks_reasoning}\n"
else:
    logger.info("instance is a legal entity")
    pass

# ============================================
# Section 8: Activity
# ============================================
logger.info("START SECTION 8: Activity -> WIP as we need to add LLM check")
if partner_info.kyc_dataset["client_type"] == "Natural Person":
    activities = partner_info.kyc_dataset.get("corporate_activity")
else:
    activities = partner_info.kyc_dataset.get("activities")

is_valid = activities is not None and len(activities) > 0
if is_valid:
    kyc_checks_output["activity"][
        "reason"
    ] += f"\n\n**{partner_name}**: Activity field(s) defined. \n"
else:
    kyc_checks_output["activity"]["status"] = False
    kyc_checks_output["activity"][
        "reason"
    ] += f"\n\n**{partner_name}**:  Activity field(s) not defined. \n"

# ============================================
# Section 10: Family situation
# ============================================
logger.info("START SECTION 10: family situation")
if partner_info.kyc_dataset["client_type"] == "Natural Person":
    family_situation_entries = partner_info.kyc_dataset.get(
        "family_situation_entries", []
    )
    family_situation_remarks = (
        partner_info.kyc_dataset.get("family_situation_remarks")
        or ""
    )

    family_situation_collapsed = "\n".join(
        [
            ", ".join([f"{k}: {v}" for k, v in entry.items()])
            for entry in family_situation_entries
        ]
    )
    family_situation_collapsed += family_situation_remarks
    family_situation_collapsed = family_situation_collapsed.strip()

    extracted_family = extract_family_members(
        str(partner_info.kyc_dataset)
    )

    formatted_family = [
        f"- Name: {x['name']}, Relation: {x['relation']}, SoW Relevant: {x['source_of_wealth_relevant']}, Politically Exposed: {x['politically_exposed']}"
        for x in extracted_family
    ]
    family_links = "\n" + "\n".join(formatted_family)

    tmp = f"Extracted family members with potential links to SoW/PEP: {family_links if len(family_links.strip()) > 0 else 'none.'}"
    headline = None

    if len(family_situation_collapsed) > 0:
        relevant_extracted_family = [
            (x, fuzz.WRatio(x, family_situation_collapsed))
            for x in extracted_family
            if x["source_of_wealth_relevant"] == "yes"
            or x["politically_exposed"] == "yes"
        ]

        cross_checking_needed = [
            x
            for x, ratio in relevant_extracted_family
            if ratio < 80
        ]

        explicit_mentions = ", ".join(
            [
                x["name"]
                for x, ratio in relevant_extracted_family
                if ratio >= 80
            ]
        )
        llm_cross_checks = ", ".join(
            [x["name"] for x in cross_checking_needed]
        )

        tmp += f"\n\nPersons explicitly mentioned in the family situation section: {explicit_mentions if len(explicit_mentions.strip()) > 0 else 'none'}."
        tmp += f"\n\nPersons needing an LLM cross check to confirm explicit mention in the family situation section: {llm_cross_checks if len(llm_cross_checks.strip()) > 0 else 'none'}.\n"
        check_ok = True
        for x in cross_checking_needed:
            llm_response = cross_check(family_situation_collapsed, x["name"])
            save_json(
                llm_response,
                output_folder,
                folder_name,
                "section10kyc_family_situation.json",
            )
            tmp += f"- {x['name']}: Mentioned: {llm_response['Answer']}, Reasoning: {llm_response['Reasoning']}\n"
            if llm_response["Answer"] != "Yes":
                kyc_checks_output["family_situation"]["status"] = False
                check_ok = False
    else:
        if len(extracted_family) > 0:
            check_ok = False
            kyc_checks_output["family_situation"]["status"] = False
            headline = "the family section is empty, which is not permitted as SoW-related or PEP-relevant persons have been identified."
        else:
            check_ok = True
            headline = "the family section is empty, which is permitted as no SoW-related or PEP-relevant persons have been identified."

    if headline is not None:
        kyc_checks_output["family_situation"][
            "reason"
        ] += f"\n\n**{partner_name}**: {headline}\n"
    elif check_ok:
        kyc_checks_output["family_situation"][
            "reason"
        ] += f"\n\n**{partner_name}**: the family section mentions all SoW-relevant and/or politically exposed persons, if any.\n"
    else:
        kyc_checks_output["family_situation"][
            "reason"
        ] += f"\n\n**{partner_name}**: the family section needs attention.\n"

    if not (headline and check_ok):
        tmp += "\n"
        kyc_checks_output["family_situation"]["reason"] += tmp
else:
    kyc_checks_output["family_situation"][
        "reason"
    ] += f"\n\n**{partner_name}**: N/A (legal entity).\n"