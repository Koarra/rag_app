"""
kyc_state.py
Shared state object passed through the KYC checks LangGraph pipeline.
Mirrors the pattern of edd_state.py.
"""

from typing import TypedDict, Dict, Any


class kyc_state(TypedDict, total=False):
    # --- Inputs (set once at the start) ---
    partner_name: str
    folder_name: str
    ou_code_mapped: str
    output_folder: str
    partner_info: Any               # parsed KYC partner object
    kyc_checks_output: Dict         # accumulated results, updated by each node

    # --- Section outputs (populated progressively by each node) ---
    purpose_of_business_relationships: Dict     # Section 3
    origin_of_asset: Dict                       # Section 4
    # Add more as sections are implemented:
    # total_assets: Dict                        # Section 6
