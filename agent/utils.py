"""
utils.py
Shared helpers: I/O, serialisation, LLM client, EDD loading, partner resolution.
"""

import os
import json
from glob import glob
from typing import Any

import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.core.credentials import get_bearer_token_provider
from llama_index.llms import AzureOpenAI


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

def build_llm() -> AzureOpenAI:
    """Instantiate and return the Azure OpenAI LLM client."""
    return AzureOpenAI(
        engine="gpt-4o",
        use_azure_ad=True,
        azure_ad_token_provider=get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        ),
    )


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def save_json(data: dict | str, output_folder: str, folder_name: str, filename: str) -> None:
    """Write *data* as JSON to output_folder/folder_name/filename."""
    output_dir = os.path.join(output_folder, folder_name)
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, filename)
    if isinstance(data, str):
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(data)
    else:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


def custom_serializer(value: Any) -> Any:
    """Fallback serialiser for non-JSON-native types."""
    if hasattr(value, "dict"):
        return value.dict()
    if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
        return list(value)
    return str(value)


def serialise_kyc_dataset(partner_info, output_folder: str, folder_name: str) -> dict:
    """Dump all non-dunder, non-callable kyc_dataset attributes to JSON."""
    excluded = {"_abc_impl", "abc_omple"}
    kyc_dict = {
        attr: custom_serializer(getattr(partner_info.kyc_dataset, attr))
        for attr in dir(partner_info.kyc_dataset)
        if (
            not (attr.startswith("__") and attr.endswith("__"))
            and attr not in excluded
            and not callable(getattr(partner_info.kyc_dataset, attr))
        )
    }
    save_json(kyc_dict, output_folder, folder_name, "kyc_pdf_parser_data.json")
    return kyc_dict


# ---------------------------------------------------------------------------
# EDD loading & partner resolution
# ---------------------------------------------------------------------------

def load_edd_case(input_folder: str, edd_text_parser) -> dict:
    """Locate and parse the EDD case file, returning the parsed case dict."""
    edd_case_path_folder = glob(input_folder + "/DD-**")[2]
    edd_case_path_ex = glob(edd_case_path_folder + "/DD-*.txt")[0]

    try:
        edd_case_path = glob(edd_case_path_folder + "/DD-*.txt")[0]
        print(f"EDD case path: {edd_case_path}")
    except IndexError:
        raise FileNotFoundError(f"No DD-*.txt file found in {edd_case_path_folder}")

    with open(edd_case_path_ex, "r", encoding="ISO-8859-1") as f:
        edd_raw_text = f.read()

    return edd_text_parser.edd_info_parsing(edd_raw_text)


def resolve_ou_mapping(edd_case: dict, ou_code_data_path: str) -> str:
    """Look up the OU name for the EDD org unit. Returns empty string on failure."""
    edd_ou = edd_case["org_unit"]
    ou_df = pd.read_csv(ou_code_data_path)[["orgUnitCode", "managingOrgUnitName"]]
    try:
        row = ou_df[ou_df["orgUnitCode"] == edd_ou]
        ou_name = row["managingOrgUnitName"].values[0]
        ou_code = row["orgUnitCode"].values[0]
        mapped = f"name - {ou_name}, code - {ou_code}"
        print(f"OU mapping found: {mapped}")
        return mapped
    except Exception:
        print("EDD OU code not found and/or mapping failed")
        return ""


def resolve_partner_info(
    kyc_to_edd_partner_matches: dict,
    client_histories_parsed: list,
    edd_name: str,
):
    """
    Find the KYC folder name and partner_info object for *edd_name*.
    Returns (kyc_folder, partner_info) — either may be None if not found.
    """
    kyc_folder = next(
        (
            r["kyc_partner_name"]
            for r in kyc_to_edd_partner_matches["mappings"]
            if r["matched_edd_name"] == edd_name
        ),
        None,
    )
    if kyc_folder:
        print("verification1 completed")

    partner_info = next(
        (info for info in client_histories_parsed if info.partner_name == kyc_folder),
        None,
    )
    if partner_info:
        print("verification2 completed")

    return kyc_folder, partner_info
