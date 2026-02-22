# ============================================
# Section 6: Total assets
# ============================================
logger.info("START SECTION 6: TOTAL ASSETS")
if partner_info.kyc_dataset["client_type"] == "Natural Person":
    logger.info("instance is individual")
    
    total_assets = partner_info.kyc_dataset.get("total_assets", {})
    total_assets_fields = total_assets.get("total_assets", {})
    
    kyc_liquidity = (
        total_assets_fields.get("cash", {}).get("number")
        if total_assets_fields.get("cash")
        else None
    )
    kyc_real_estate = (
        total_assets_fields.get("real_estate", {}).get("number")
        if total_assets_fields.get("real_estate")
        else None
    )
    kyc_non_liquid = (
        total_assets_fields.get("non_liquid", {}).get("number")
        if total_assets_fields.get("non_liquid")
        else None
    )
    kyc_total_assets = (
        total_assets_fields.get("total", {}).get("number")
        if total_assets_fields.get("total")
        else None
    )
    kyc_origin_of_assets = (
        str(partner_info.kyc_dataset.get("origin_of_assets"))
        if partner_info.kyc_dataset.get("origin_of_assets")
        else "No kyc origin of assets extracted."
    )

    logger.info("proceed with assets comparisons")
    data = evaluate_total_assets(kyc_origin_of_assets)
    save_json(data, output_folder, folder_name, "section6_kyc_total_assets.json")

    amount_kyc_origin_of_assets = data["kyc_origin_of_assets"]

    total_of_specific_asset_fields = (
        (kyc_liquidity or 0)
        + (kyc_real_estate or 0)
        + (kyc_non_liquid or 0)
    )

    if not kyc_total_assets or kyc_total_assets == 0:
        percentage_of_specific_asset_fields_explaining_total_assets = 0
        percentage_of_total_assets_with_known_origin = 0
        kyc_checks_output["percentage_total_assets_explained"]["status"] = False
        kyc_checks_output["percentage_total_assets_explained"][
            "reason"
        ] += f"\n\n**{partner_name}** \nThe total assets denominator is null or zero, cannot calculate percentages.\n\n"
        logger.info("Cannot calculate percentages - denominator is null/zero.")
    else:
        percentage_of_specific_asset_fields_explaining_total_assets = (
            total_of_specific_asset_fields / kyc_total_assets
        )
        percentage_of_total_assets_with_known_origin = (
            amount_kyc_origin_of_assets / kyc_total_assets
        )

        validation_percentage = 0.8
        if (
            percentage_of_total_assets_with_known_origin >= validation_percentage
            and percentage_of_specific_asset_fields_explaining_total_assets >= validation_percentage
        ):
            logger.info(
                f"successfull check: percentage of specific asset fields composing to total assets >= 0.8: {percentage_of_specific_asset_fields_explaining_total_assets}"
            )
            logger.info(
                f"successfull check: percentage of total assets with known origin >= 0.8: {percentage_of_total_assets_with_known_origin}"
            )
            kyc_checks_output["percentage_total_assets_explained"][
                "reason"
            ] += f"\n\n**{partner_name}**\nBoth of the below percentages is above the 80% threshold.\n\n"
        else:
            logger.info("Low percentage of total asset verification")
            kyc_checks_output["percentage_total_assets_explained"]["status"] = False
            kyc_checks_output["percentage_total_assets_explained"][
                "reason"
            ] += f"\n\n**{partner_name}**\nAt least one of the below percentages is under the 80% threshold.\n\n"

        kyc_checks_output["percentage_total_assets_explained"][
            "reason"
        ] += f"The sum of **liquid** ({(kyc_liquidity or 0) :0,.2f}), **real estate** ({(kyc_real_estate or 0) :0,.2f}), **non-liquid** ({(kyc_non_liquid or 0) :0,.2f}) asset fields is {total_of_specific_asset_fields :0,.2f}, representing **{percentage_of_specific_asset_fields_explaining_total_assets:.2%}** of the total assets indicated in KYC ({kyc_total_assets :0,.2f}).\n\n"
        kyc_checks_output["percentage_total_assets_explained"][
            "reason"
        ] += f"The Origin of Assets section indicates a total assets amount of {amount_kyc_origin_of_assets :0,.2f}, representing **{percentage_of_total_assets_with_known_origin:.2%}** of the total assets indicated in KYC ({kyc_total_assets :0,.2f}).\n"
else:
    logger.info("instance is a legal entity")
    pass