"""
checks.py
All KYC section check functions.
Each run_sectionN() function runs its checks and updates kyc_checks_output in-place.
"""

from llama_index.program import LLMTextCompletionProgram

from kyc_agent.models import (
    PurposeOfBusinessRelationship,
    CheckTransactionSummary,
    CompletenessOriginOfAssets,
)
from kyc_agent.utils import save_json
from kyc_agent.prompts import (
    COMPARE_TRANSACTIONS_PURPOSE_OF_BR_PROMPT,
    SUMMARIZE_TRANSACTIONS_PROMPT,
    ORIGIN_OF_ASSET_PROMPT,
)


# ---------------------------------------------------------------------------
# Section 3: Purpose of Business Relationship
# ---------------------------------------------------------------------------

def _check_transactions_vs_purpose_of_br(
    kyc_purpose_of_br: str, kyc_transactions: str, llm
) -> PurposeOfBusinessRelationship:
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=PurposeOfBusinessRelationship,
        llm=llm,
        prompt_template_str=COMPARE_TRANSACTIONS_PURPOSE_OF_BR_PROMPT,
        verbose=False,
    )
    return program(purpose_of_br=kyc_purpose_of_br, transactions=kyc_transactions)


def _summarise_transactions(kyc_transactions: str, llm) -> CheckTransactionSummary:
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=CheckTransactionSummary,
        llm=llm,
        prompt_template_str=SUMMARIZE_TRANSACTIONS_PROMPT,
        verbose=False,
    )
    return program(kyc_transactions=kyc_transactions)


def run_section3(
    partner_info,
    partner_name: str,
    folder_name: str,
    ou_code_mapped: str,
    kyc_checks_output: dict,
    output_folder: str,
    llm,
) -> None:
    """Section 3: Purpose of the Business Relationship (checks 3.1, 3.2, 3.3)."""
    print("START SECTION 3: Purpose of the business relationship")

    kyc_transactions = partner_info.kyc_dataset["transactions"]
    kyc_purpose_of_br = partner_info.kyc_dataset["purpose_of_br"]
    kyc_transactions_str = str(kyc_transactions) if kyc_transactions else "No kyc transactions extracted"
    kyc_purpose_of_br_str = str(kyc_purpose_of_br) if kyc_purpose_of_br else "No kyc purpose of br text extracted"

    # Check 3.1 — BR vs transactions
    print("check 3.1 started")
    result_31 = _check_transactions_vs_purpose_of_br(kyc_purpose_of_br_str, kyc_transactions_str, llm)
    save_json(result_31.json(), output_folder, folder_name, "section3_kyc_transactions_purpose_of_br.json")

    if not result_31.sufficient_explanation:
        kyc_checks_output["purpose_of_business_relationships"]["status"] = False
    statement = (
        "The purpose of BR is in line with the additional information provided by KYC."
        if result_31.sufficient_explanation
        else "The purpose of BR is not in line with the additional information provided by KYC."
    )
    kyc_checks_output["purpose_of_business_relationships"]["reason"] += (
        f"\n\n**{partner_name}**\n{statement}\n"
        f"\n**Reasoning**: {result_31.reasoning}\n"
    )
    print("check 3.1 succeeded")

    # Check 3.2 — OU mapping
    print("check 3.2 started")
    if not ou_code_mapped:
        kyc_checks_output["purpose_of_business_relationships"]["reason"] += (
            f"\n**OU code mapping**: is NULL or empty or mapping did not work: {ou_code_mapped}\n"
        )
    else:
        kyc_checks_output["purpose_of_business_relationships"]["reason"] += (
            f"\n**OU code mapping found**: {ou_code_mapped}\n"
        )
    print("check 3.2 succeeded")

    # Check 3.3 — Transaction summary
    print("check 3.3 started")
    trx_summary = _summarise_transactions(kyc_transactions_str, llm)
    save_json(trx_summary.json(), output_folder, folder_name, "section3_kyc_transactions_summary.json")

    trx_lines = [str(x).strip() for x in trx_summary.transactions_details if str(x).strip()]
    trx_details = "\n".join(trx_lines) if trx_lines else "No transactions extracted."
    kyc_checks_output["purpose_of_business_relationships"]["reason"] += (
        f"\n**KYC transaction summary:**\n{trx_details}\n\n"
    )
    print("check 3.3 succeeded")


# ---------------------------------------------------------------------------
# Section 4: Origin of Assets
# ---------------------------------------------------------------------------

def _check_origin_of_assets_completeness(origin_of_assets: str, llm) -> CompletenessOriginOfAssets:
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=CompletenessOriginOfAssets,
        llm=llm,
        prompt_template_str=ORIGIN_OF_ASSET_PROMPT,
        verbose=False,
    )
    return program(origin_of_assets=origin_of_assets)


def run_section4(
    partner_info,
    partner_name: str,
    folder_name: str,
    kyc_checks_output: dict,
    output_folder: str,
    llm,
) -> None:
    """Section 4: Origin of Assets completeness check."""
    origins = partner_info.kyc_dataset.get("origin_of_assets")
    origin_of_assets = str(origins) if origins else "No origins extracted."

    oa_result = _check_origin_of_assets_completeness(origin_of_assets, llm)
    save_json(oa_result.json(), output_folder, folder_name, "section4_origin_of_assets_llm.json")

    if oa_result.complete:
        kyc_checks_output["origin_of_asset"]["reason"] += (
            f"\n\n**{partner_name}**\nOrigin of assets description is complete.\n\n"
        )
    else:
        kyc_checks_output["origin_of_asset"]["status"] = False
        kyc_checks_output["origin_of_asset"]["reason"] += (
            f"\n\n**{partner_name}**\nOrigin of assets description is incomplete.\n\n"
        )
    kyc_checks_output["origin_of_asset"]["reason"] += f"**Reasoning**: {oa_result.reason}\n"
