if key == "consistency_checks_within_kyc_contradiction_checks":
    for k, v in value.items():
        print(f"  key: {k}, type: {type(v)}, value: {v if not isinstance(v, dict) else list(v.keys())}")
