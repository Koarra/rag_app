if key == "consistency_checks_within_kyc_contradiction_checks":
    cell = row_cells[2]
    cell.add_paragraph("Please refer to the annex for LLM analysis details.\n")
    
    reason = value.get("reason", "")
    checks = []
    for line in reason.split("\n"):
        if line.startswith("**") and "**" in line[2:]:
            check_name = line.split("**")[1]
            no_contradiction = "no contradictions identified" in line.lower()
            checks.append({
                "check": check_name.title(),
                "contradictions_present": str(not no_contradiction)
            })
    
    if checks:
        self.add_subtable(cell, checks)
else:
    reason = str(value.get("reason", ""))
    self.write_bold_instances(row_cells[2], reason.strip())
