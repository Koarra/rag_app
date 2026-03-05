# If processing KYC checks, add the status indicator
            if not is_edd:
                check_status = value.get("status", False) if isinstance(value, dict) else False
                colour = RGBColor(0, 255, 0) if check_status else RGBColor(255, 0, 0)
                reason_text = value.get("reason", "") if isinstance(value, dict) else str(value)
                if reason_text == "Out of scope currently.":
                    colour = RGBColor(211, 211, 211)
                self.set_cell_color(row_cells[0], colour)

                if key == "consistency_checks_within_kyc_contradiction_checks":
                    cell = row_cells[2]
                    cell.add_paragraph("Please refer to the annex for LLM analysis details.\n")
                    raw_checks = value.get("raw_checks", {}) if isinstance(value, dict) else {}
                    checks = [
                        {
                            "check": k.replace("_", " ").title(),
                            "contradictions_present": str(v.get("contradictory", "No") == "Yes")
                        }
                        for k, v in raw_checks.items()
                    ]
                    if checks:
                        self.add_subtable(cell, checks)
                else:
                    self.write_bold_instances(row_cells[2], reason_text.strip())
