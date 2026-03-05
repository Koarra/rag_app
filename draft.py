for partner_name, partner_checks in kyc_profiles_output.items():
    doc.add_paragraph().add_run(partner_name).bold = True
    self.create_table(doc, partner_checks, is_edd=False)
