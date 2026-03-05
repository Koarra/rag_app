# Merge reasons from all partners into a single checks dict
merged_checks = list(kyc_profiles_output.values())[0].copy()
for key in merged_checks:
    if key == "consistency_checks_within_kyc_contradiction_checks":
        continue
    combined_reason = "\n".join(
        f"**{partner_name}**: {partner_checks.get(key, {}).get('reason', '')}"
        for partner_name, partner_checks in kyc_profiles_output.items()
        if partner_checks.get(key, {}).get("reason", "")
    )
    if combined_reason:
        merged_checks[key] = dict(merged_checks[key])
        merged_checks[key]["reason"] = combined_reason

self.create_table(
    doc,
    merged_checks,
    is_edd=False,
    all_partners_checks=all_partners_checks,
)
```

This way, for each non-11.2 row, the cell will show:
```
Partner A: <reason from partner A>
Partner B: <reason from partner B>
