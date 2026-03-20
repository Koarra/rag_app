kyc_transactions = partner_info.kyc_dataset["transactions"]
kyc_purpose_of_br = partner_info.kyc_dataset["purpose_of_br"]

kyc_transactions_str = (
    str(kyc_transactions) if kyc_transactions else "No kyc transactions extracted"
)
kyc_purpose_of_br_str = (
    str(kyc_purpose_of_br)
    if kyc_purpose_of_br
    else "No kyc purpose of br text extracted"
)

# ✅ ADD THIS GUARD — before any LLM call
if not kyc_transactions:
    logger.info("check 3.1 skipped: no KYC transactions present")
    purpose_of_br_result = PurposeOfBusinessRelationship(
        sufficient_explanation=True,  # nothing to contradict, so pass
        reasoning="Skipped: no KYC transactions found for this partner."
    )
    # still write the output so downstream code doesn't break
    save_json(
        purpose_of_br_result.json(),
        output_folder,
        folder_name,
        section3_kyc_transactions_purpose_of_br,
    )
    kyc_checks_output["purpose_of_business_relationships"]["status"] = True
    return  # or continue to check 3.2

# --- only reaches here if transactions exist ---
logger.info("check 3.1 started")
purpose_of_business_relationship_prompt = (
    COMPARE_TRANSACTIONS_PURPOSE_OF_BR_PROMPT.format(
        kyc_purpose_of_br=kyc_purpose_of_br_str,
        kyc_transactions=kyc_transactions_str,
    )
)
purpose_of_br_result = run_compliance_check(
    purpose_of_business_relationship_prompt, PurposeOfBusinessRelationship
)








# Run once, reuse across checks 3.1 and 3.3
if not kyc_transactions:
    transaction_summary = CheckTransactionSummary(
        transactions_exist=False,
        transactions_details=[]
    )
else:
    # call LLM to summarize (check 3.3)
    transaction_summary = run_compliance_check(..., CheckTransactionSummary)

# Now check 3.1 can safely branch
if not transaction_summary.transactions_exist:
    # skip with default result
else:
    # run full LLM check
