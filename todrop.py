# total_of_specific_asset_fields = amount_kyc_liquid_assets + amount_kyc_liquid_real_estate_assets + amount_kyc_liquid_other_non_liquid_assets

total_of_specific_asset_fields = (kyc_liquidity or 0) + (kyc_real_estate or 0) + (kyc_non_liquid or 0)

# Check if denominator is valid
if not kyc_total_assets or kyc_total_assets == 0:
    percentage_of_specific_asset_fields_explaining_total_assets = 0
    percentage_of_total_assets_with_known_origin = 0
    kyc_checks_output["percentage_total_assets_explained"]["status"] = False
    kyc_checks_output["percentage_total_assets_explained"]["reason"] += kyc_partner_name + " \n Total assets denominator is null or zero, cannot calculate percentage. \n"
    print("Cannot calculate percentages - denominator is null/zero")
else:
    # Calculate percentages
    percentage_of_specific_asset_fields_explaining_total_assets = total_of_specific_asset_fields / kyc_total_assets
    percentage_of_total_assets_with_known_origin = amount_kyc_origin_of_assets / kyc_total_assets
    
    # Validate percentages
    validation_percentage = 0.8
    if percentage_of_total_assets_with_known_origin >= validation_percentage and percentage_of_specific_asset_fields_explaining_total_assets > validation_percentage:
        print("successfull check: percentage of specific asset fields composing to total assets >= 0.8", percentage_of_specific_asset_fields_explaining_total_assets)
        print("successfull check: percentage of total assets with known origin >= 0.8", percentage_of_total_assets_with_known_origin)
        kyc_checks_output["percentage_total_assets_explained"]["reason"] += kyc_partner_name + " \n An high percentage of the total assets has known origins.. \n"
        kyc_checks_output["percentage_total_assets_explained"]["status"] = True
    else:
        print("Low percentage of total asset verification")
        kyc_checks_output["percentage_total_assets_explained"]["status"] = False
        kyc_checks_output["percentage_total_assets_explained"]["reason"] += kyc_partner_name + " \n A low percentage of the total assets has known origins.: \n"

print("percentage of total assets", percentage_of_total_assets_with_known_origin)
print(f"{'='*80}\n")
