for partner_info in client_histories_parsed:
    print("Available attributes:", dir(partner_info.kyc_dataset))
    print("Instance type:", type(partner_info.kyc_dataset))
