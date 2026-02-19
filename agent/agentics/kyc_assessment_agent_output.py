"""
kyc_assessment_agent_output.py
LangGraph pipeline for KYC quality checks.
Mirrors the pattern of edd_assessment_agent_output.py.

Each node corresponds to one KYC section check. Nodes read from and write
back to the shared kyc_state, progressively enriching it.
"""

from langgraph.graph import StateGraph, END

from kyc_agent.kyc_state import kyc_state
from kyc_agent.kyc_checks_nodes import (
    node_section3_purpose_of_br,
    node_section4_origin_of_assets,
    # node_section6_total_assets,   # add as sections are implemented
)
from kyc_agent.utils import build_llm


class kyc_assessment_agent_output:
    """LangGraph-based KYC quality checks pipeline."""

    def __init__(self):
        self.llm = build_llm()

        self.graph = StateGraph(kyc_state)

        # --- Add nodes ---
        # LLM-powered checks use lambda to inject the llm dependency,
        # matching the same pattern as edd_assessment_agent_output.
        self.graph.add_node(
            "section3_purpose_of_br",
            lambda s: node_section3_purpose_of_br(s, self.llm),
        )
        self.graph.add_node(
            "section4_origin_of_assets",
            lambda s: node_section4_origin_of_assets(s, self.llm),
        )
        # self.graph.add_node(
        #     "section6_total_assets",
        #     lambda s: node_section6_total_assets(s, self.llm),
        # )

        # --- Define execution order ---
        self.graph.set_entry_point("section3_purpose_of_br")
        self.graph.add_edge("section3_purpose_of_br", "section4_origin_of_assets")
        self.graph.add_edge("section4_origin_of_assets", END)
        # self.graph.add_edge("section4_origin_of_assets", "section6_total_assets")
        # self.graph.add_edge("section6_total_assets", END)

        self.agent = self.graph.compile()
