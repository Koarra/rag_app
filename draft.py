if kyc_profiles_output:
    print(f"KYC top-level keys: {list(kyc_profiles_output.keys())}")
    print(f"KYC type: {type(kyc_profiles_output)}")
    
    first_key = list(kyc_profiles_output.keys())[0]
    first_value = kyc_profiles_output[first_key]
    print(f"First key: {first_key}")
    print(f"First value type: {type(first_value)}")
    print(f"First value keys: {list(first_value.keys()) if isinstance(first_value, dict) else first_value}")
    
    if isinstance(first_value, dict):
        second_key = list(first_value.keys())[0]
        second_value = first_value[second_key]
        print(f"Second level key: {second_key}")
        print(f"Second level value type: {type(second_value)}")
        print(f"Second level value: {second_value}")

    # Create KYC checks Header and table
    kyc_heading = doc.add_heading("KYC Checks", level=2)
    kyc_heading.alignment = 1  # Center the heading
    self.create_table(doc, kyc_profiles_output, is_edd=False)
