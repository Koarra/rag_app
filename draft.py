# Fill the table with dictionary keys and values
        i = 0
        for key, value in processed_profile_output.items():
            if key in skip_keys:
                continue

            row_cells = table.rows[i].cells
            i += 1

            # Get the display name for the key
            if is_edd:
                display_name = self.get_display_name(key, is_req_c, is_edd=True)
            else:
                display_name = value.get("display_name", key.replace("_", " ").capitalize()) if isinstance(value, dict) else key.replace("_", " ").capitalize()

            idx = 0 if is_edd else 1
            row_cells[idx].add_paragraph().add_run(display_name).bold = True

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
                    checks = []
                    for line in reason_text.split("\n"):
                        line = line.strip()
                        if "vs rest**" in line.lower():
                            check_name = line.split("**")[0].replace("**", "").strip().title()
                            contradictory = "no contradictions" not in line.lower()
                            checks.append({
                                "check": check_name,
                                "contradictions_present": str(contradictory)
                            })
                    if checks:
                        self.add_subtable(cell, checks)
                else:
                    self.write_bold_instances(row_cells[2], reason_text.strip())

            elif key not in ["activity", "total_wealth_composition"]:
                self.write_bold_instances(row_cells[1], value.strip() if isinstance(value, str) else str(value))

            elif key == "activity":
                cell = row_cells[1]
                for partner_name, activities in processed_profile_output.get(
                    "raw_data", {}
                ).get("activity", {}).items():
                    _ = cell.add_paragraph().add_run(f"{partner_name}\n").bold = True
                    self.add_subtable(cell, activities)

            elif key == "total_wealth_composition":
                cell = row_cells[1]
                for partner_name, twc_dict in processed_profile_output.get(
                    "raw_data", {}
                ).get("total_wealth_composition", {}).items():
                    cell.add_paragraph().add_run(f"\n{partner_name}\n").bold = True

                    sub_table_keys = [
                        "bankable_assets",
                        "private_equity",
                        "real_estate",
                        "other_assets",
                    ]
                    sub_table_names = [
                        "Bankable assets",
                        "Private equity assets",
                        "Real estate assets",
                        "Other assets",
                    ]

                    for sub_key, name in zip(sub_table_keys, sub_table_names):
                        cell.add_paragraph(name + ":")
                        self.add_subtable(cell, twc_dict.get(sub_key, {}).get("assets", []))
