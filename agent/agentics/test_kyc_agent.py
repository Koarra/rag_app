# test_kyc_agent.py

from kyc_agent.kyc_assessment_agent_output import kyc_assessment_agent_output

# --- Mock partner_info with minimal fake data ---
class MockKycDataset:
    def __getitem__(self, key):
        return {
            "transactions": "Client received 500k CHF from real estate sale in 2023.",
            "purpose_of_br": "Investment management and wealth preservation.",
            "origin_of_assets": "Real estate sale proceeds and inheritance from parents.",
        }.get(key, "")

    def get(self, key, default=None):
        return self[key] or default

class MockPartnerInfo:
    partner_name = "Test Partner"
    kyc_folder_path = "/tmp/test_partner"
    kyc_dataset = MockKycDataset()

# --- Build initial state ---
initial_kyc_state = {
    "partner_name": "Test Partner",
    "folder_name": "TEST-001/Test Partner",
    "ou_code_mapped": "name - Zurich WM, code - CH001",
    "output_folder": "/tmp/kyc_test_output",
    "partner_info": MockPartnerInfo(),
    "kyc_checks_output": {
        "purpose_of_business_relationships": {"status": True, "reason": "", "display_name": "3. Purpose of Business Relationship"},
        "origin_of_asset": {"status": True, "reason": "", "display_name": "4. Origin of Assets"},
    },
}

# --- Run agent ---
print("Building KYC agent...")
agent = kyc_assessment_agent_output().agent

print("Running KYC agent...")
final_state = agent.invoke(initial_kyc_state)

# --- Print results ---
print("\n=== RESULTS ===")
for section, result in final_state["kyc_checks_output"].items():
    print(f"\n[{section}]")
    print(f"  Status : {result['status']}")
    print(f"  Reason : {result['reason'][:200]}...")  # truncate for readability