    def _merge_kyc_checks(self, kyc_profiles_output: dict) -> dict:
        """Merge KYC check results from all partners into a single dict.

        For each check key, builds a combined reason string with each partner's
        name in bold followed by their reason. The display_name and status are
        taken from the first partner's entry.

        Args:
            kyc_profiles_output: dict
                {partner_name: {check_key: {status, reason, display_name, ...}}}

        Returns:
            merged_checks: dict with same structure as a single partner's checks,
            but with reasons merged across all partners.
        """
        template = list(kyc_profiles_output.values())[0]
        merged_checks = {}

        for key, value in template.items():
            # Section 11.2 is handled separately via all_partners_checks
            if key == "consistency_checks_within_kyc_contradiction_checks":
                merged_checks[key] = value
                continue

            if not isinstance(value, dict):
                merged_checks[key] = value
                continue

            # Build combined reason from all partners
            reasons = []
            for partner_name, partner_checks in kyc_profiles_output.items():
                partner_value = partner_checks.get(key, {})
                reason = partner_value.get("reason", "") if isinstance(partner_value, dict) else ""
                if reason:
                    reasons.append(f"**{partner_name}**: {reason}")

            merged_checks[key] = {
                "display_name": value.get("display_name", key.replace("_", " ").capitalize()),
                "status": value.get("status", False),
                "reason": "\n".join(reasons),
            }

        return merged_checks
