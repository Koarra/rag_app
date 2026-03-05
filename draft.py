"""Module for formatting EDD assessment and KYC quality check results into a Word report."""

import os

from constants import OUTPUT_FOLDER
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Cm, Pt, RGBColor


class output_writer:
    """Class for formatting EDD assessment and KYC quality check results into a Word report."""

    def create_output_folder(self):
        """Create an output folder with the current date and time."""
        self.output_folder = OUTPUT_FOLDER
        os.makedirs(self.output_folder, exist_ok=True)

    def get_display_name(self, key: str, is_req_c: bool = False, is_edd: bool = False):
        """Return the display name of the given key."""
        display_names_edd = {
            "type_of_business_relationship": "1. Type of Business Relationship",
            "request_type": "2. Request Type",
            "risk_category": "3. Risk Category",
            "purpose_of_business_relationship": "4. Purpose of Business Relationship",
            "expected_nnm_or_current_aum": (
                "5. Current AUM" if is_req_c else "5. Expected NNM"
            ),
            "expected_transactions": (
                "6. Transactions" if is_req_c else "6. Expected Transactions"
            ),
            "activity": "7. Activity",
            "total_wealth_composition": "8. Total Wealth Composition",
            "source_of_wealth": "9. Source of Wealth",
            "corroboration": "10. Corroboration",
            "negative_news": "11. Negative News and Assessment/Screening Results",
            "other_risk_aspects": "12. Other Risk Aspects and Potentially Mitigating Factors",
            "other_relevant_information": "13. Other Relevant Information",
            "final_summary": "14. Final Summary",
        }

        if is_edd:
            return display_names_edd.get(key, key.replace("_", " ").capitalize())

    def create_table(
        self,
        doc: Document,
        processed_profile_output: dict,
        is_edd: bool = False,
    ):
        """Populate the given document with the EDD assessment / KYC check results."""
        cols = 2 if is_edd else 3
        doc.add_paragraph()  # Small line break before the table

        # EDD has metadata keys to skip, KYC partner_checks has none
        if is_edd:
            skip_keys = {"dict_parsed_text", "raw_data", "file_path", "raw_text"}
        else:
            skip_keys = set()

        num_rows = sum(1 for k in processed_profile_output if k not in skip_keys)

        if num_rows == 0:
            return

        table = doc.add_table(rows=num_rows, cols=cols, style="Table Grid")
        table.style.paragraph_format.space_after = Pt(5)

        is_req_c = (
            is_edd and "Request Type C" in processed_profile_output.get("request_type", "")
        )

        original_width = 1.4 * (table.columns[0].cells[0].width)

        if not is_edd:
            original_width -= Cm(0.5)
            for cell in table.columns[0].cells:
                cell.width = Cm(0.5)

        for cell in table.columns[-2].cells:
            cell.width = 0.6 * cell.width

        for cell in table.columns[-1].cells:
            cell.width += original_width

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
                display_name = value.get("display_name", key.replace("_", " ").capitalize())

            idx = 0 if is_edd else 1
            row_cells[idx].add_paragraph().add_run(display_name).bold = True

            # If processing KYC checks, add the status indicator
            if not is_edd:
                check_status = value.get("status", False)
                colour = RGBColor(0, 255, 0) if check_status else RGBColor(255, 0, 0)
                if value.get("reason", "") == "Out of scope currently.":
                    colour = RGBColor(211, 211, 211)
                self.set_cell_color(row_cells[0], colour)

                if key != "consistency_checks_within_kyc_contradiction_checks":
                    reason = str(value.get("reason", ""))
                    self.write_bold_instances(row_cells[2], reason.strip())
                else:
                    cell = row_cells[2]
                    cell.add_paragraph("Please refer to the annex for LLM analysis details.\n")
                    raw_data = processed_profile_output.get("raw_data", {})
                    contradiction_checks = raw_data.get(
                        "consistency_checks_within_kyc_contradiction_checks", {}
                    )
                    for partner_name, checks in contradiction_checks.items():
                        _ = cell.add_paragraph().add_run(f"{partner_name}\n").bold = True
                        self.add_subtable(cell, checks)

            elif key not in ["activity", "total_wealth_composition"]:
                self.write_bold_instances(row_cells[1], value.strip())

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

    def add_subtable(self, cell, values):
        if not values:
            return

        column_names = [k.title().replace("_", " ") for k in values[0].keys()]
        sub_table = cell.add_table(rows=len(values) + 1, cols=len(column_names))
        sub_table.style = "Light Grid"
        sub_table.style.font.size = Pt(10)

        for _cell, name in zip(sub_table.rows[0].cells, column_names):
            _cell.text = name

        for idx, elems in enumerate(values, start=1):
            for _cell, (k, v) in zip(sub_table.rows[idx].cells, elems.items()):
                _cell.text = v.title().replace("_", " ")

                if _cell.text == "True":
                    self.set_cell_color(_cell, "#DC3939")
                elif _cell.text == "False":
                    self.set_cell_color(_cell, "#29B95C")

    def set_cell_color(self, cell, color):
        """Apply a solid background colour to a table cell."""
        if isinstance(color, str):
            hex_color = color.lstrip("#")
        else:
            if hasattr(color, "rgb"):
                hex_color = f"{color.rgb:06x}"
            elif isinstance(color, (int,)):
                hex_color = f"{color:06x}"
            elif isinstance(color, (list, tuple)) and len(color) == 3:
                r, g, b = color
                hex_color = f"{r:02x}{g:02x}{b:02x}"
            else:
                raise TypeError(
                    f"Unable to convert colour {color!r} to a hex string. "
                    "Supported inputs: RGBColor, (r,g,b) tuple/list, int, or hex string."
                )

        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._element.get_or_add_tcPr().append(shading_elm)

    def write_bold_instances(self, document: Document, text: str):
        """Write a given text, bolding strings surrounded by double asterisks (**like this**)."""
        for para in text.replace("\n\n", "\n").split("\n"):
            is_bold = False
            run = document.add_paragraph()
            run.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY_LOW
            for chunk in para.split("**"):
                _ = run.add_run(chunk)
                _.bold = is_bold
                is_bold = not is_bold

    def write_word_doc(
        self,
        edd_profile_output: dict,
        kyc_profiles_output: dict,
        case_number: str,
        partner_mappings: dict,
        edd_case: dict,
    ):
        """Write the EDD assessment and KYC quality check results in a Word report."""
        doc = Document()

        # Title
        doc.add_heading(
            "EDD Assessment/KYC checks - Business Relationship " + case_number + "\n",
            level=1,
        )

        # Partners section
        doc.add_paragraph("EDD case partners & roles", style="Subtitle")
        doc.add_paragraph(
            edd_case["contractual_partner_information"]["name"]
            + " - contractual partner, \n"
            + ",\n".join(
                [
                    item["name"] + " - " + item["role"].replace("has ", "")
                    for item in edd_case["role_holders_information"]
                ]
            )
        )

        if partner_mappings:
            doc.add_paragraph("KYC Partners", style="Subtitle")
            doc.add_paragraph(
                "With KYC history:\n"
                + ",\n".join(
                    [
                        " - " + item
                        for item in partner_mappings["partner_folder_names_with_kyc"]
                    ]
                )
            )

            doc.add_paragraph(
                "Without KYC history:\n"
                + ",\n".join(
                    [
                        " - " + item
                        for item in partner_mappings["partner_folder_names_without_kyc"]
                    ]
                )
            )

            doc.add_paragraph(
                "Without EDD entry:\n"
                + ",\n".join(
                    [
                        " - " + item["kyc_partner_name"]
                        for item in partner_mappings["mappings"]
                        if item["match_status"] == "unmatched"
                    ]
                )
            )

        # KYC Checks section — one table per partner
        if kyc_profiles_output:
            kyc_heading = doc.add_heading("KYC Checks", level=2)
            kyc_heading.alignment = 1
            for partner_name, partner_checks in kyc_profiles_output.items():
                doc.add_paragraph().add_run(partner_name).bold = True
                self.create_table(doc, partner_checks, is_edd=False)

        # EDD Assessment section
        if edd_profile_output:
            doc.add_page_break()
            edd_heading = doc.add_heading("EDD Assessment", level=2)
            edd_heading.alignment = 1
            self.create_table(doc, edd_profile_output, is_edd=True)

        # Annex section — one entry per partner
        if kyc_profiles_output:
            doc.add_page_break()
            doc.add_heading("Annex", level=2).alignment = 1
            doc.add_paragraph().add_run("KYC Check 11.2 Analysis").bold = True

            for partner_name, partner_checks in kyc_profiles_output.items():
                print(f"Processing annex for partner: {partner_name}")
                doc.add_paragraph().add_run(partner_name).bold = True

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

                if checks:
                    column_names = list(checks[0].keys())
                    table = doc.add_table(rows=len(checks) + 1, cols=len(column_names), style="Light Grid")
                    for _cell, name in zip(table.rows[0].cells, column_names):
                        _cell.text = name.title().replace("_", " ")
                    for idx, row_data in enumerate(checks, start=1):
                        for _cell, val in zip(table.rows[idx].cells, row_data.values()):
                            _cell.text = str(val)
                    print(f"Table created for {partner_name}")

                doc.add_paragraph()
                self.write_bold_instances(doc, contradiction_value.get("reason", ""))
                doc.add_paragraph()

        # Save document
        save_path = os.path.join(self.output_folder, case_number)
        os.makedirs(save_path, exist_ok=True)
        run_date = OUTPUT_FOLDER.split("/")[-1]
        doc.save(os.path.join(save_path, f"Report_BR_{case_number}_{run_date}.docx"))
