# At the top of the file, add these imports
from utils.func_utils import get_llm
from coreruler.data_abstractions.query import Query
from constants import PARTNER_NAME_MATCHING_PROMPT, PARTNER_NAME_MATCHING_ARGS
import json
import os

def match_partner_name(kyc_partner_name, edd_partner_names):
    """
    Use LLM to match a KYC partner name with the most likely EDD partner name.
    Returns the matched EDD partner name or None if no match found.
    """
    llm_partner_matcher = get_llm(PARTNER_NAME_MATCHING_ARGS)
    
    # Format the EDD partner names as a bulleted list
    edd_partner_list = "\n".join(f"- {name}" for name in edd_partner_names)
    
    query = Query(
        query_setup=PARTNER_NAME_MATCHING_PROMPT,
        model=llm_partner_matcher,
        system_prompt="You are a name matching assistant. Always return valid JSON."
    )
    
    result = query.invoke({
        "kyc_partner_name": kyc_partner_name,
        "edd_partner_list": edd_partner_list
    })
    
    # Parse the JSON result
    try:
        match_result = json.loads(result)
        matched_name = match_result.get("matched_name")
        confidence = match_result.get("confidence")
        reason = match_result.get("reason")
        
        print(f"  Confidence: {confidence}")
        print(f"  Reason: {reason}")
        
        # Validate that the matched name is in the list and confidence is acceptable
        if matched_name and matched_name in edd_partner_names and confidence in ["high", "medium"]:
            return matched_name
        else:
            return None
            
    except json.JSONDecodeError as e:
        print(f"  ✗ Error parsing LLM response: {e}")
        print(f"  Raw response: {result}")
        return None


# Then update your processing method:
@staticmethod
def processing(client_histories_parsed, edd_parsed, edd_txt_dic):
    
    # Get all partner names from EDD total_wealth_composition
    edd_partner_names = list(edd_txt_dic.get("total_wealth_composition", {}).keys())
    
    print(f"\nEDD Partners found in text file: {edd_partner_names}")
    print(f"{'='*80}\n")
    
    # Match each KYC partner with EDD partners
    for partner_info in client_histories_parsed:
        folder_name = os.path.basename(partner_info.kyc_folder_path)
        kyc_partner_name = partner_info.kyc_dataset.name
        
        print(f"Processing KYC folder: {folder_name}")
        print(f"KYC Partner Name: {kyc_partner_name}")
        
        # Use LLM to match with EDD partner
        matched_edd_name = match_partner_name(kyc_partner_name, edd_partner_names)
        
        if matched_edd_name:
            print(f"✓ Matched with EDD partner: {matched_edd_name}")
            
            # Add folder name to the matched EDD partner's data
            edd_txt_dic["total_wealth_composition"][matched_edd_name]["kyc_folder_name"] = folder_name
            edd_txt_dic["total_wealth_composition"][matched_edd_name]["kyc_partner_name"] = kyc_partner_name
        else:
            print(f"✗ No match found for KYC partner: {kyc_partner_name}")
        
        print(f"{'-'*80}\n")
    
    # Continue with your existing processing.
        
        
        
        
        
        
        
        root ::= match_result

match_result ::= "{" ws "\"matched_name\":" ws matched_name_value "," ws "\"confidence\":" ws confidence_value "," ws "\"reason\":" ws string ws "}"

matched_name_value ::= string | "null"

confidence_value ::= "\"high\"" | "\"medium\"" | "\"low\"" | "\"none\""

string ::=
  "\"" (
    [^"\\\x00-\x1F] |
    "\\" (["\\/bfnrt] | "u" [0-9a-fA-F]{4})
  )* "\"" ws

ws ::= (" " | "\n" | "\t")*..






# Partner Name Matching
PARTNER_NAME_MATCHING_PROMPT = """You are helping match partner names from different data sources.

KYC Partner Name: {kyc_partner_name}

EDD Partner Names (from text file):
{edd_partner_list}

Task: Which EDD partner name most likely refers to the same person/entity as the KYC partner name?

Output format: Return a JSON object with the following structure:
{{
    "matched_name": "exact EDD partner name from the list",
    "confidence": "high/medium/low",
    "reason": "brief explanation of why they match"
}}

If no match is found, return:
{{
    "matched_name": null,
    "confidence": "none",
    "reason": "explanation of why no match"
}}

Return ONLY valid JSON, no additional text."""

PARTNER_NAME_MATCHING_ARGS = {
    "model": DEFAULT_MODEL,
    "size": "12b",
    "llama_cpp_kwargs": {
        "grammar": (GRAMMARS / "partner_name_matching.gbnf").read_text(),
        "seed": 420,
        "temperature": 0.0,
    },
}
    # ... rest of your code
