"""
agent_orchestrator.py
Runs and saves the results of the EDD assessment and KYC quality checks.
"""

import logging
import os
from glob import glob

from constants import OUTPUT_FOLDER, OU_CODE_DATA_PATH
from output_writer import output_writer
from edd_agent.edd_text_parser import edd_text_parser
from edd_agent.edd_assessment_agent_output import edd_assessment_agent_output
from kyc_agent.kyc_assessment_agent_output import kyc_assessment_agent_output
from kyc_agent.process_kyc_pdf import process_kyc_pdf
from kyc_agent.utils import resolve_ou_mapping, serialise_kyc_dataset
from kyc_agent.pipeline import (
    KYC_CHECK_KEYS,
    OUT_OF_SCOPE_CHECKS,
)
from utils.fuzzy_match import match_and_save_partners
from utils.func_utils import save_json
from utils.logger_config import setup_logger

logger = setup_logger(__name__)

DICT_KYC_CHECKS_NAME_DISPLAY = {
    "sign_off": "1. Sign-Off",
    "additional_sign_offs": "2. Additional Sign-Offs",
    "purpose_of_business_relationships": "3. Purpose of Business Relationship",
    "origin_of_asset": "4. Origin of Assets",
    "corroboration": "5. Corroboration and Evidence",
    "percentage_total_assets_explained": "6. Total Assets / Composition of Assets",
    "remarks_on_total_assets_and_composition": "7. Remarks on Total Assets and Asset Composition",
    "activity": "8. Activity",
    "transactions": "9. Transactions",
    "family_situation": "10. Family Situation",
    "consistency_checks_within_kyc": "11.1 Consistency Checks within the KYC - role holders and ASM numbers",
    "consistency_checks_within_kyc_contradiction_checks": "11.2 Consistency Checks within the KYC - contradiction checks: one field vs other fields",
    "consistency_checks_with_previous_edd": "12. Consistency Checks with Previous EDD Assessment",
    "scap_flags": "13. SCAP Flags",
    "siap_flags": "14. SIAP Flags",
}


class agent_orchestrator:
    """Runs the EDD assessment and KYC quality checks for a given EDD case."""

    def __init__(self, edd_case_path: str):
        """
        Args:
            edd_case_path: Path to the EDD case folder to be processed.
        """
        logger.info("=" * 60)
        logger.info("Initializing EDD Analysis")
        logger.info("=" * 60)

        # --- Locate DD text file ---
        try:
            self.edd_case_path = glob(edd_case_path + "/DD-*.txt")[0]
            logger.info(f"EDD case path: {self.edd_case_path}")
        except IndexError:
            logger.error(f"No DD-*.txt file found in {edd_case_path}")
            raise FileNotFoundError(f"No DD-*.txt file found in {edd_case_path}")

        self.case_number = edd_case_path.split("/")[-1]
        logger.info(f"Case number: {self.case_number}")

        self.partner_folders = glob(edd_case_path + "/Partners/*")
        self.pep_documents_present = (
            len(glob(edd_case_path + "/Sensitivity Attachments/PEP/*")) > 0
        )

        if not self.partner_folders:
            logger.warning("No partner folders found")
        else:
            logger.info(f"Found {len(self.partner_folders)} partner folders")

        # --- Parse EDD text ---
        with open(self.edd_case_path, "r", encoding="ISO-8859-1") as f:
            self.edd_raw_text = f.read()
            self.edd_case = edd_text_parser.edd_info_parsing(self.edd_raw_text)

        # --- Process KYC PDFs ---
        self.kyc_cases = [
            process_kyc_pdf(partner_folder)
            for partner_folder in self.partner_folders
        ]

        logger.info("Starting analysis pipeline")
        self.run_analysis()
        self.write_results()

    def _init_kyc_checks_output(self) -> dict:
        """Initialise the kyc_checks_output dict with status, reason and display_name."""
        kyc_checks_output = {}
        for check_name, display_name in DICT_KYC_CHECKS_NAME_DISPLAY.items():
            kyc_checks_output[check_name] = {
                "status": True,
                "reason": "",
                "display_name": display_name,
            }
            if check_name in OUT_OF_SCOPE_CHECKS:
                kyc_checks_output[check_name]["reason"] = "Out of scope currently."
        return kyc_checks_output

    def run_analysis(self):
        """Run the EDD assessment and KYC quality checks."""

        # --- EDD analysis ---
        save_json(self.edd_case, OUTPUT_FOLDER, self.case_number, "edd_text_parser.json")
        logger.info("Intermediate data saved for edd_txt_parser")

        logger.info("Starting EddAssessmentOutput")
        initial_edd_state = {
            "file_path": self.edd_case_path,
            "raw_text": self.edd_raw_text,
            "dict_parsed_text": self.edd_case,
        }
        edd_agent = edd_assessment_agent_output().agent
        self.edd_result = edd_agent.invoke(initial_edd_state)

        save_json(self.edd_result, OUTPUT_FOLDER, self.case_number, "edd_assessment_agent_output.json")
        logger.info("Intermediate data saved for edd result")

        # --- KYC analysis ---
        logger.info("Starting KYC checks output processing")

        # Extract partner names from EDD case
        edd_partner_names = [
            partner["name"]
            for partner in self.edd_case.get("total_wealth_composition", [])
        ]
        edd_name = self.edd_case["contractual_partner_information"]["name"]
        ou_code_mapped = resolve_ou_mapping(self.edd_case, ou_code_data_path=OU_CODE_DATA_PATH)

        # Fuzzy match KYC partners to EDD partners
        self.partner_mappings = match_and_save_partners(
            self.kyc_cases,
            edd_partner_names,
            threshold=0.8,
            output_path=os.path.join(
                OUTPUT_FOLDER, self.case_number, "partner_name_mapping.json"
            ),
            verbose=True,
        )

        # Filter out KYC cases with empty datasets
        client_histories_parsed = [
            item for item in self.kyc_cases if item.kyc_dataset is not None
        ]
        logger.info(f"Valid KYC histories: {len(client_histories_parsed)}")

        # Initialise shared output structure
        kyc_checks_output = self._init_kyc_checks_output()

        # Build the KYC LangGraph agent (once, shared across all partners)
        kyc_agent = kyc_assessment_agent_output().agent

        # Run KYC checks for each EDD partner
        self.kyc_results = {}
        for partner_name_edd in edd_partner_names:
            logger.info(f"Running KYC checks for partner: {partner_name_edd}")

            # Find the matching KYC partner_info
            kyc_folder = next(
                (
                    r["kyc_partner_name"]
                    for r in self.partner_mappings["mappings"]
                    if r["matched_edd_name"] == partner_name_edd
                ),
                None,
            )
            partner_info = next(
                (
                    info
                    for info in client_histories_parsed
                    if info.partner_name == kyc_folder
                ),
                None,
            )

            if not kyc_folder or not partner_info:
                logger.warning(f"Could not resolve partner info for: {partner_name_edd}")
                continue

            folder_name = os.path.join(
                self.case_number,
                os.path.basename(partner_info.kyc_folder_path),
            )

            # Serialise KYC dataset to disk
            serialise_kyc_dataset(partner_info, OUTPUT_FOLDER, folder_name)

            # Build initial KYC state
            initial_kyc_state = {
                "partner_name": partner_info.partner_name,
                "folder_name": folder_name,
                "ou_code_mapped": ou_code_mapped,
                "output_folder": OUTPUT_FOLDER,
                "partner_info": partner_info,
                "kyc_checks_output": kyc_checks_output,
            }

            # Run the LangGraph KYC pipeline
            final_kyc_state = kyc_agent.invoke(initial_kyc_state)
            self.kyc_results[partner_name_edd] = final_kyc_state["kyc_checks_output"]

            save_json(
                self.kyc_results[partner_name_edd],
                OUTPUT_FOLDER,
                folder_name,
                "kyc_checks_output.json",
            )
            logger.info(f"KYC checks completed for: {partner_name_edd}")

        logger.info("run analysis completed successfully")

    def write_results(self):
        """Write the results into a formatted Word report."""
        logger.info("Writing final results")
        self.writer = output_writer()
        self.writer.create_output_folder()
        self.writer.write_word_doc(
            self.edd_result,
            self.kyc_results,
            self.case_number,
            self.partner_mappings,
            self.edd_case,
        )
