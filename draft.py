    excluded_keys = {"client_type"}
    kyc_dict = {
        k: v
        for k, v in partner_info.kyc_dataset.items()
        if k not in excluded_keys
        and v is not None
        and v != ""
        and v != []
    }
