"""
kyc_checks_nodes.py
LangGraph node wrappers for each KYC section check.

Each function takes the shared kyc_state, calls the underlying check logic,
updates kyc_checks_output, and returns the updated state — exactly the same
pattern as nodes in edd_assessment_agent_output.py.
"""

from kyc_agent.kyc_state import kyc_state
from kyc_agent.checks import run_section3, run_section4


def node_section3_purpose_of_br(state: kyc_state, llm) -> kyc_state:
    """LangGraph node: Section 3 — Purpose of Business Relationship."""
    run_section3(
        partner_info=state["partner_info"],
        partner_name=state["partner_name"],
        folder_name=state["folder_name"],
        ou_code_mapped=state["ou_code_mapped"],
        kyc_checks_output=state["kyc_checks_output"],
        output_folder=state["output_folder"],
        llm=llm,
    )
    return {
        **state,
        "purpose_of_business_relationships": state["kyc_checks_output"]["purpose_of_business_relationships"],
    }


def node_section4_origin_of_assets(state: kyc_state, llm) -> kyc_state:
    """LangGraph node: Section 4 — Origin of Assets."""
    run_section4(
        partner_info=state["partner_info"],
        partner_name=state["partner_name"],
        folder_name=state["folder_name"],
        kyc_checks_output=state["kyc_checks_output"],
        output_folder=state["output_folder"],
        llm=llm,
    )
    return {
        **state,
        "origin_of_asset": state["kyc_checks_output"]["origin_of_asset"],
    }


# --- Template for adding new sections ---
# def node_section6_total_assets(state: kyc_state, llm) -> kyc_state:
#     """LangGraph node: Section 6 — Total Assets."""
#     run_section6(
#         partner_info=state["partner_info"],
#         partner_name=state["partner_name"],
#         folder_name=state["folder_name"],
#         kyc_checks_output=state["kyc_checks_output"],
#         output_folder=state["output_folder"],
#         llm=llm,
#     )
#     return {
#         **state,
#         "total_assets": state["kyc_checks_output"]["total_assets"],
#     }
