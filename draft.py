for partner_name, partner_checks in kyc_profiles_output.items():
    print(f"Processing partner: {partner_name}")
    contradiction_value = partner_checks.get(
        "consistency_checks_within_kyc_contradiction_checks", {}
    )
    raw_checks = contradiction_value.get("raw_checks", {})
    print(f"raw_checks keys: {list(raw_checks.keys())}")
    print(f"raw_checks length: {len(raw_checks)}")
    checks = [
        {
            "check": k.replace("_", " ").title(),
            "contradictions_present": str(v.get("contradictory", "No") == "Yes")
        }
        for k, v in raw_checks.items()
    ]
    print(f"checks length: {len(checks)}")
    if checks:
        print(f"Adding subtable for {partner_name}")
        self.add_subtable(doc, checks)
    self.write_bold_instances(doc, contradiction_value.get("reason", ""))
