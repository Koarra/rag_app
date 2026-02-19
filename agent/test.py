from neuralkyc.data.datasets.legal_entity import LegalEntity

edd_case_path_folder = glob(INPUT_FOLDER + "/DD-**")[2]
edd_case_path_ex = glob(edd_case_path_folder + "/DD-*.txt")[0]
try:
    edd_case_path = glob(edd_case_path_folder + "/DD-*.txt")[0]
    print(f"EDD case path: {edd_case_path}")
except IndexError:
    print(f"No DD-*.txt file found in {edd_case_path_folder}")
    raise FileNotFoundError(f"No DD-*.txt file found in {edd_case_path_folder}")

with open(edd_case_path_ex, "r", encoding="ISO-8859-1") as f:
    edd_raw_text = f.read()
    edd_case = edd_text_parser.edd_info_parsing(edd_raw_text)

print(edd_case)
####
# Get all partner names from EDD total_wealth_composition (it's a list)
total_wealth_comp_list = edd_case.get("total_wealth_composition", [])
print("TOTAL WEALTH")
print(total_wealth_comp_list)
# Extract just the partner names from the list
edd_partner_names = [partner["name"] for partner in total_wealth_comp_list]
# load EDD br text parsed to get the BU extracted and type of BR
edd_ou = edd_case["org_unit"]
ou_df = pd.read_csv(OU_CODE_DATA_PATH)  # load csv file to map to OU name
ou_df = ou_df[["orgUnitCode", "managingOrgUnitName"]]

print("step1")
try:
    matching_row = ou_df[ou_df["orgUnitCode"] == edd_ou]

    edd_ou_name = matching_row["managingOrgUnitName"].values[0]
    edd_ou_code = matching_row["orgUnitCode"].values[0]

    ou_code_mapped = f"name - {edd_ou_name}, code - {edd_ou_code}"
    print(
        f"edd OU name and edd ou managingOrgUnitName: {ou_code_mapped}"
    )
except Exception as e:
    ou_code_mapped = ""
    print("EDD OU code not found and/or mapping failed")

kyc_checks_output = {}
raw_data = {"consistency_checks_within_kyc_contradiction_checks": {}}
dict_kyc_checks_name_display = {
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

kyc_folder = None
for match_record in kyc_to_edd_partner_matches["mappings"]:
    if match_record["matched_edd_name"] == edd_name:
        print("verification1 completed")
        kyc_folder = match_record["kyc_partner_name"]
        break

partner_info = None
for info in client_histories_parsed:
    print("info", info)
    if info.partner_name == kyc_folder:
        print("e")
        print(info.partner_name)
        print("verification2 completed")
        partner_info = info
        break

print("HERE")
print(kyc_folder)
print(partner_info)

if kyc_folder is not None and partner_info is not None:
    print("HERE2")
    print(f"Available attributes: {dir(partner_info.kyc_dataset)}")
    # logger.info(f"Instance type: {type(partner_info.kyc_dataset)}")
    folder_name = os.path.basename(partner_info.kyc_folder_path)
    # logger.info(f"FOLDER NAME: {folder_name}")
    partner_name = partner_info.partner_name
    folder_name = os.path.join(case_number, folder_name)


# =============================================
# Section 3: Purpose of the business relationship (for contracting partner only)
# =============================================
print("START SECTION 3: Purpose of the business relationship")

# Check 1: compare the purpose of BR is in line with the additional information provided by kyc
print("check 3.1 started")
print(partner_info)
kyc_transactions = partner_info.kyc_dataset["transactions"]
kyc_purpose_of_br = partner_info.kyc_dataset["purpose_of_br"]
print("kyc_transactions", kyc_transactions)
print("kyc_purpose_of_br", kyc_purpose_of_br)
kyc_transactions_str = (
    str(kyc_transactions)
    if kyc_transactions
    else "No kyc transactions extracted"
)

kyc_purpose_of_br_str = (
    str(kyc_purpose_of_br)
    if kyc_purpose_of_br
    else "No kyc purpose of br text extracted"
)

class PurposeOfBusinessRelationship(BaseModel):
    sufficient_explanation: bool = Field(description="Whether the details provided in kyc purpose of br justify the transaction value present in kyc transactions")
    reasoning: str = Field(description="The reason behind the explanation robustness")

llm = AzureOpenAI(
    engine="gpt-4o",
    use_azure_ad=True,
    azure_ad_token_provider=get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
)


def check_transactions_in_line_with_purpose_of_br(kyc_purpose_of_br, kyc_transactions, llm):
    """Extract persons and companies using LlamaIndex"""

    # Limit text to 15000 characters
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=PurposeOfBusinessRelationship,
        llm=llm,
        prompt_template_str=COMPARE_TRANSACTIONS_PURPOSE_OF_BR_PROMPT,
        verbose=False
    )

    result = program(purpose_of_br=kyc_purpose_of_br, transactions=kyc_transactions)
    return result


# TODO HERE
# llm_response_transactions_in_line_with_purpose_of_br = (
#     check_transactions_in_line_with_purpose_of_br(
#         kyc_purpose_of_br_str, kyc_transactions_str
#     )
# )

result = check_transactions_in_line_with_purpose_of_br(kyc_purpose_of_br_str, kyc_transactions_str, llm)
print(type(result))

print(result)
print("save json")
save_json(
    result.json(),
    OUTPUT_FOLDER,
    folder_name,
    "section3_kyc_transactions_purpose_of_br.json",
)
print(
    "Intermediate data saved: data kyc transactions comparison with purpose of br"
)

transactions_sufficiency_checks = result.sufficient_explanation
transactions_sufficiency_checks_reasoning = result.reasoning

# Final check
statement = "The purpose of BR is in line with the additional information provided by KYC."
if not transactions_sufficiency_checks:
    kyc_checks_output["purpose_of_business_relationships"]["status"] = False
    statement = "The purpose of BR is not in line with the additional information provided by KYC."

kyc_checks_output["purpose_of_business_relationships"][
    "reason"
] += f"\n\n**{partner_name}**\n{statement}\n"
kyc_checks_output["purpose_of_business_relationships"][
    "reason"
] += f"\n**Reasoning**: {transactions_sufficiency_checks_reasoning}\n"

print("check 3.1 succeeded")
# next step: check this condition is True or False

# Check 2: add to the reasoning the information related to OU and the adequate mapping related to it
print("check 3.2 started")
if ou_code_mapped == "" or ou_code_mapped is None:
    kyc_checks_output["purpose_of_business_relationships"][
        "reason"
    ] += f"\n**OU code mapping**: is NULL or empty or mapping did not work: {ou_code_mapped} \n"
else:
    kyc_checks_output["purpose_of_business_relationships"][
        "reason"
    ] += f"\n**OU code mapping found**: {ou_code_mapped}\n"

print("check 3.2 succeeded")

# Check 3: Summarize the transactions from bottom of client history for reference
print("check 3.3 started")
# TODO HERE

class TransactionDetail(BaseModel):
    amount: float = Field(description="Transaction amount")
    date: str = Field(description="Transaction date in YYYY-MM-DD format")
    currency: str = Field(description="Transaction currency code (e.g., USD, EUR)")

class CheckTransactionSummary(BaseModel):
    transactions_exist: bool = Field(description="True if any transactions are found, otherwise False")
    transactions_details: List[TransactionDetail] = Field(
        description="A list of summarized transactions with amount, date, and currency"
    )


def check_transaction_summary(kyc_transactions, llm):
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=CheckTransactionSummary,
        llm=llm,
        prompt_template_str=SUMMARIZE_TRANSACTIONS_PROMPT,
        verbose=False
    )

    result = program(kyc_transactions=kyc_transactions)
    return result


llm_response_kyc_transaction_summary = check_transaction_summary(
    kyc_transactions_str, llm
)
print("THIS STEP")
print(kyc_transactions_str)
print(llm_response_kyc_transaction_summary)
save_json(
    llm_response_kyc_transaction_summary.json(),
    OUTPUT_FOLDER,
    folder_name,
    "section3_kyc_transactions_summary.json",
)
print("Intermediate data saved: kyc transactions summarized")

trx_summaries = [
    str(x).strip()
    for x in llm_response_kyc_transaction_summary.transactions_details
    if len(str(x).strip()) > 0
]
trx_details = (
    "\n".join(trx_summaries)
    if len(trx_summaries) > 0
    else "No transactions extracted."
)

kyc_checks_output["purpose_of_business_relationships"][
    "reason"
] += "\n**KYC transaction summary:**"
kyc_checks_output["purpose_of_business_relationships"][
    "reason"
] += f"\n{trx_details}\n\n"

trx_summaries = [
    str(x).strip()
    for x in llm_response_kyc_transaction_summary.transactions_details
    if len(str(x).strip()) > 0
]
trx_details = (
    "\n".join(trx_summaries)
    if len(trx_summaries) > 0
    else "No transactions extracted."
)

for partner_info in client_histories_parsed:
    iteration += 1
    # Create a dictionary with attributes that do not have double underscores at the start or end
    print(f"Available attributes: {dir(partner_info.kyc_dataset)}")
    print(f"Instance type: {type(partner_info.kyc_dataset)}")
    folder_name = os.path.basename(partner_info.kyc_folder_path)
    print(f"FOLDER NAME: {folder_name}")
    partner_name = partner_info.partner_name
    folder_name = os.path.join(case_number, folder_name)

    kyc_dict = {}

    excluded_attributes = {"_abc_impl", "abc_omple"}

    for attr in dir(partner_info.kyc_dataset):
        # Exclude attributes with double underscores, specific excluded attributes, and callable methods
        if (
            not (attr.startswith("__") and attr.endswith("__"))
            and attr not in excluded_attributes
        ):
            value = getattr(partner_info.kyc_dataset, attr)
            if not callable(value):  # Exclude methods
                kyc_dict[attr] = custom_serializer(value)

    output_dir = os.path.join(OUTPUT_FOLDER, folder_name)
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "kyc_pdf_parser_data.json")
    with open(save_path, "w", encoding="utf-8") as json_file:
        json.dump(kyc_dict, json_file, indent=4, ensure_ascii=False)

    # =============================================
    # Section 4: Origin of assets
    # =============================================
    origins = partner_info.kyc_dataset.get("origin_of_assets")
    origin_of_assets = str(origins) if origins else "No origins extracted."
    # TODO HERE

    class completeness_origin_of_assets(BaseModel):
        complete: bool = Field(description="Whether the origin of assets is complete or not")
        reason: str = Field(description="The reason behind the completion status")

    def origin_of_assets_completeness(text, llm):
        # Limit text to 15000 characters
        program = LLMTextCompletionProgram.from_defaults(
            output_cls=completeness_origin_of_assets,
            llm=llm,
            prompt_template_str=ORIGIN_OF_ASSET_PROMPT,
            verbose=False
        )

        result = program(origin_of_assets=origin_of_assets)
        return result

    oa_llm_result = origin_of_assets_completeness(origin_of_assets, llm)

    save_json(
        oa_llm_result.json(),
        OUTPUT_FOLDER,
        folder_name,
        "section4_origin_of_assets_llm.json",
    )

    if oa_llm_result.complete == "true":
        kyc_checks_output["origin_of_asset"][
            "reason"
        ] += f"\n\n**{partner_name}**\nOrigin of assets description is complete.\n\n"
    else:
        kyc_checks_output["origin_of_asset"]["status"] = False
        kyc_checks_output["origin_of_asset"][
            "reason"
        ] += f"\n\n**{partner_name}**\nOrigin of assets description is incomplete.\n\n"

    kyc_checks_output["origin_of_asset"]["reason"] += (
        "**Reasoning**: " + oa_llm_result.reason + "\n"
    )

    # =============================================
    # Section 6: Total assets
    # =============================================