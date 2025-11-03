   else:
        print("Low percentage of total asset verification")
        kyc_checks_output["percentage_total_assets_explained"]["status"] = False
        kyc_checks_output["percentage_total_assets_explained"]["reason"] += kyc_partner_name + " \n A low percentage of the total assets has known origins.: \n"
