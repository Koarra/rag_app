# Annex section — one entry per partner
        if kyc_profiles_output:
            doc.add_page_break()
            doc.add_heading("Annex", level=2).alignment = 1
            doc.add_paragraph().add_run("KYC Check 11.2 Analysis").bold = True

            for partner_name, partner_checks in kyc_profiles_output.items():
                print(f"Processing annex for partner: {partner_name}")
                contradiction_value = partner_checks.get(
                    "consistency_checks_within_kyc_contradiction_checks", {}
                )
                raw_checks = contradiction_value.get("raw_checks", {})
                print(f"raw_checks length: {len(raw_checks)}")
                checks = [
                    {
                        "check": k.replace("_", " ").title(),
                        "contradictions_present": str(v.get("contradictory", "No") == "Yes")
                    }
                    for k, v in raw_checks.items()
                ]
                print(f"checks for {partner_name}: {checks}")

                doc.add_paragraph().add_run(partner_name).bold = True
                if checks:
                    column_names = list(checks[0].keys())
                    table = doc.add_table(rows=len(checks) + 1, cols=len(column_names), style="Light Grid")
                    for _cell, name in zip(table.rows[0].cells, column_names):
                        _cell.text = name.title().replace("_", " ")
                    for idx, row_data in enumerate(checks, start=1):
                        for _cell, val in zip(table.rows[idx].cells, row_data.values()):
                            _cell.text = str(val)

                self.write_bold_instances(doc, contradiction_value.get("reason", ""))
