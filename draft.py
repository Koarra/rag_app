# Attach raw contradiction checks data
import json
contradiction_path = os.path.join(
    OUTPUT_FOLDER, folder_name, "section11_2_kyc_data_check_kyc_contradiction.json"
)
if os.path.exists(contradiction_path):
    with open(contradiction_path) as f:
        self.kyc_results[partner_name_edd][
            "consistency_checks_within_kyc_contradiction_checks"
        ]["raw_checks"] = json.load(f)
