raw_data = processed_profile_output.get("raw_data", {})
contradiction_checks = raw_data.get("consistency_checks_within_kyc_contradiction_checks", {})
for partner_name, checks in contradiction_checks.items():for partner_name, partner_checks in kyc_profiles_output.items():
    doc.add_paragraph().add_run(partner_name).bold = True
    self.create_table(doc, partner_checks, is_edd=False)



# activity - line ~151
for partner_name, activities in processed_profile_output.get("raw_data", {}).get("activity", {}).items():

# total_wealth_composition - line ~158
for partner_name, twc_dict in processed_profile_output.get("raw_data", {}).get("total_wealth_composition", {}).items():
