total_assets_list = partner_info.kyc_dataset.get('total_assets', {}).get('Total estimated assets') or []
total_assets_value = total_assets_list[0].number if total_assets_list else None
f"KYC_TOTAL_ASSETS : {total_assets_value}"
