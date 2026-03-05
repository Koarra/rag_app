def write_results(self):
    logger.info("Writing final results")
    self.writer = output_writer()
    self.writer.create_output_folder()

    # Merge KYC results across all partners
    kyc_profiles_output = {}
    for partner_name, checks in self.kyc_results.items():
        for check_name, check_data in checks.items():
            if check_name not in kyc_profiles_output:
                # First partner - initialise the check
                kyc_profiles_output[check_name] = check_data.copy()
                kyc_profiles_output[check_name]["reason"] = (
                    f"{partner_name}:\n{check_data['reason']}"
                )
            else:
                # Subsequent partners - append reason and take worst status
                kyc_profiles_output[check_name]["reason"] += (
                    f"\n\n{partner_name}:\n{check_data['reason']}"
                )
                if not check_data["status"]:
                    kyc_profiles_output[check_name]["status"] = False

    self.writer.write_word_doc(
        self.edd_result,
        kyc_profiles_output,
        self.case_number,
        self.partner_mappings,
        self.edd_case,
    )
