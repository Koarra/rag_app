for partner_name, partner_checks in kyc_profiles_output.items():
    doc.add_paragraph().add_run(partner_name).bold = True
    contradiction_value = partner_checks.get(
        "consistency_checks_within_kyc_contradiction_checks", {}
    )
    raw_checks = contradiction_value.get("raw_checks", {})
    checks = [
        {
            "check": k.replace("_", " ").title(),
            "contradictions_present": str(v.get("contradictory", "No") == "Yes")
        }
        for k, v in raw_checks.items()
    ]
    if checks:
        self.add_subtable(doc, checks)
    self.write_bold_instances(doc, contradiction_value.get("reason", ""))
