"""
Stage 4: Risk Analysis and Crime Flagging
Identifies entities involved in money laundering and sanctions evasion
"""
import sys
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).parent.parent))

from src.utils import Config, OpenAIClient, FileHandler


class RiskAnalyzer:
    def __init__(self, api_key: str = None):
        self.openai_client = OpenAIClient(api_key)
        self.file_handler = FileHandler()

        # Define crime indicators for prompt
        self.money_laundering_indicators = [
            "Unusual or complex transaction patterns",
            "Use of shell companies or front companies",
            "Layering activities (multiple transfers to obscure origin)",
            "Structuring/Smurfing (breaking large amounts into smaller ones)",
            "Transactions with high-risk jurisdictions",
            "Cash-intensive businesses",
            "Rapid movement of funds",
            "Inconsistent business activities",
            "Use of nominees or third parties to conceal ownership",
            "Trade-based money laundering"
        ]

        self.sanctions_evasion_indicators = [
            "Transactions with sanctioned countries/jurisdictions",
            "Use of front companies to hide beneficiaries",
            "Re-routing through third countries",
            "False documentation or mislabeling of goods",
            "Involvement of sanctioned individuals or entities",
            "Use of cryptocurrencies to avoid detection",
            "Trade in prohibited goods or dual-use items",
            "Ship-to-ship transfers",
            "Use of aliases or shell companies",
            "Complex corporate structures to obscure ownership"
        ]

    def analyze_risks(
        self,
        document_text: str,
        entities: Dict[str, List[str]],
        entity_descriptions: Dict[str, Dict],
        document_name: str
    ) -> Dict:
        """
        Analyze document and entities for crime indicators

        Args:
            document_text: Full document text
            entities: Dictionary with persons and companies
            entity_descriptions: Entity descriptions from Stage 3
            document_name: Name of document

        Returns:
            Risk assessment results
        """
        print(f"\n{'='*60}")
        print(f"STAGE 4: RISK ANALYSIS")
        print(f"{'='*60}")
        print(f"Analyzing risks in: {document_name}")

        # Step 1: Document-level risk assessment
        print("\nStep 1: Analyzing document for crime indicators...")
        document_risk = self._analyze_document_risk(document_text)

        # Step 2: Entity-level risk assessment
        print("Step 2: Analyzing individual entities...")
        entity_risks = self._analyze_entity_risks(
            document_text,
            entities,
            entity_descriptions
        )

        # Step 3: Compile final risk report
        risk_report = self._compile_risk_report(
            document_risk,
            entity_risks,
            document_name
        )

        return risk_report

    def _analyze_document_risk(self, document_text: str) -> Dict:
        """
        Perform document-level risk analysis

        Args:
            document_text: Full document text

        Returns:
            Document risk assessment
        """
        # Truncate if needed
        max_length = 15000
        if len(document_text) > max_length:
            doc_sample = document_text[:max_length]
        else:
            doc_sample = document_text

        json_schema = {
            "name": "document_risk_assessment",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "overall_risk_level": {
                        "type": "string",
                        "enum": ["high", "medium", "low", "none"],
                        "description": "Overall risk level of the document"
                    },
                    "money_laundering_risk": {
                        "type": "string",
                        "enum": ["high", "medium", "low", "none"]
                    },
                    "sanctions_evasion_risk": {
                        "type": "string",
                        "enum": ["high", "medium", "low", "none"]
                    },
                    "red_flags": {
                        "type": "array",
                        "description": "List of specific red flags identified",
                        "items": {"type": "string"}
                    },
                    "suspicious_patterns": {
                        "type": "array",
                        "description": "Suspicious patterns or behaviors identified",
                        "items": {"type": "string"}
                    },
                    "analysis_summary": {
                        "type": "string",
                        "description": "Brief summary of the risk analysis"
                    }
                },
                "required": [
                    "overall_risk_level",
                    "money_laundering_risk",
                    "sanctions_evasion_risk",
                    "red_flags",
                    "suspicious_patterns",
                    "analysis_summary"
                ],
                "additionalProperties": False
            }
        }

        ml_indicators = "\n".join(f"  • {ind}" for ind in self.money_laundering_indicators)
        se_indicators = "\n".join(f"  • {ind}" for ind in self.sanctions_evasion_indicators)

        messages = [
            {
                "role": "system",
                "content": f"""You are an expert financial crime analyst specializing in anti-money laundering (AML) and sanctions compliance.

Analyze documents for indicators of:

MONEY LAUNDERING INDICATORS:
{ml_indicators}

SANCTIONS EVASION INDICATORS:
{se_indicators}

Provide objective, evidence-based analysis. Flag genuine concerns but avoid false positives."""
            },
            {
                "role": "user",
                "content": f"""Analyze this document for money laundering and sanctions evasion indicators.

Document:
{doc_sample}

Provide a comprehensive risk assessment with specific red flags and evidence."""
            }
        ]

        return self.openai_client.chat_completion_json(
            messages=messages,
            model=Config.RISK_ANALYSIS_MODEL,
            json_schema=json_schema,
            temperature=0.1,  # Low temperature for consistency
            max_tokens=1500
        )

    def _analyze_entity_risks(
        self,
        document_text: str,
        entities: Dict[str, List[str]],
        entity_descriptions: Dict[str, Dict]
    ) -> List[Dict]:
        """
        Analyze individual entities for risk indicators

        Args:
            document_text: Full document text
            entities: Extracted entities
            entity_descriptions: Entity descriptions

        Returns:
            List of flagged entities with risk details
        """
        all_entity_names = entities.get('persons', []) + entities.get('companies', [])

        if not all_entity_names:
            return []

        # Process in batches
        batch_size = 5
        flagged_entities = []

        for i in range(0, len(all_entity_names), batch_size):
            batch = all_entity_names[i:i+batch_size]
            batch_risks = self._analyze_entity_batch(
                batch,
                document_text,
                entity_descriptions
            )
            flagged_entities.extend(batch_risks)

        return flagged_entities

    def _analyze_entity_batch(
        self,
        entity_names: List[str],
        document_text: str,
        entity_descriptions: Dict[str, Dict]
    ) -> List[Dict]:
        """Analyze a batch of entities for risks"""

        # Prepare entity context
        entity_contexts = []
        for name in entity_names:
            desc = entity_descriptions.get(name, {})
            context = f"""
Entity: {name}
Type: {desc.get('type', 'unknown')}
Role: {desc.get('role', 'unknown')}
Description: {desc.get('description', 'No description available')}
Activities: {', '.join(desc.get('key_activities', []))}
Financial Details: {desc.get('financial_details', 'None')}
"""
            entity_contexts.append(context)

        combined_context = "\n---\n".join(entity_contexts)

        json_schema = {
            "name": "entity_risk_assessment",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "flagged_entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_name": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "crimes_flagged": {
                                    "type": "array",
                                    "description": "List of crimes: money_laundering, sanctions_evasion, or both",
                                    "items": {
                                        "type": "string",
                                        "enum": ["money_laundering", "sanctions_evasion"]
                                    }
                                },
                                "risk_level": {
                                    "type": "string",
                                    "enum": ["high", "medium", "low"]
                                },
                                "confidence": {
                                    "type": "number",
                                    "description": "Confidence score 0-1"
                                },
                                "evidence": {
                                    "type": "array",
                                    "description": "Specific evidence from document",
                                    "items": {"type": "string"}
                                },
                                "reasoning": {
                                    "type": "string",
                                    "description": "Explanation of why entity is flagged"
                                }
                            },
                            "required": [
                                "entity_name",
                                "entity_type",
                                "crimes_flagged",
                                "risk_level",
                                "confidence",
                                "evidence",
                                "reasoning"
                            ],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["flagged_entities"],
                "additionalProperties": False
            }
        }

        messages = [
            {
                "role": "system",
                "content": """You are an expert in financial crime detection. Analyze entities for involvement in:
1. Money Laundering
2. Sanctions Evasion

Only flag entities with credible evidence from the document. Be thorough but avoid false positives.
Provide confidence scores based on strength of evidence."""
            },
            {
                "role": "user",
                "content": f"""Analyze these entities for money laundering and sanctions evasion indicators:

{combined_context}

Flag only entities with credible evidence of involvement in these crimes.
For each flagged entity, provide specific evidence and reasoning."""
            }
        ]

        try:
            result = self.openai_client.chat_completion_json(
                messages=messages,
                model=Config.RISK_ANALYSIS_MODEL,
                json_schema=json_schema,
                temperature=0.1,
                max_tokens=2000
            )
            return result.get('flagged_entities', [])
        except Exception as e:
            print(f"Error analyzing entity batch: {e}")
            return []

    def _compile_risk_report(
        self,
        document_risk: Dict,
        entity_risks: List[Dict],
        document_name: str
    ) -> Dict:
        """
        Compile final risk report

        Args:
            document_risk: Document-level risk assessment
            entity_risks: List of flagged entities
            document_name: Name of document

        Returns:
            Compiled risk report
        """
        # Count entities by risk level and crime type
        high_risk_count = sum(1 for e in entity_risks if e['risk_level'] == 'high')
        medium_risk_count = sum(1 for e in entity_risks if e['risk_level'] == 'medium')

        ml_entities = [e for e in entity_risks if 'money_laundering' in e['crimes_flagged']]
        se_entities = [e for e in entity_risks if 'sanctions_evasion' in e['crimes_flagged']]

        report = {
            "document_name": document_name,
            "document_risk_assessment": {
                "overall_risk_level": document_risk['overall_risk_level'],
                "money_laundering_risk": document_risk['money_laundering_risk'],
                "sanctions_evasion_risk": document_risk['sanctions_evasion_risk'],
                "red_flags": document_risk['red_flags'],
                "suspicious_patterns": document_risk['suspicious_patterns'],
                "analysis_summary": document_risk['analysis_summary']
            },
            "entity_risk_summary": {
                "total_flagged": len(entity_risks),
                "high_risk": high_risk_count,
                "medium_risk": medium_risk_count,
                "money_laundering_flags": len(ml_entities),
                "sanctions_evasion_flags": len(se_entities)
            },
            "flagged_entities": entity_risks
        }

        print(f"\n✓ Risk Analysis Complete:")
        print(f"  - Document Risk: {document_risk['overall_risk_level'].upper()}")
        print(f"  - Flagged Entities: {len(entity_risks)}")
        print(f"  - Money Laundering Flags: {len(ml_entities)}")
        print(f"  - Sanctions Evasion Flags: {len(se_entities)}")

        return report

    def process(
        self,
        document_text: str,
        entities: Dict[str, List[str]],
        entity_descriptions: Dict[str, Dict],
        document_name: str,
        file_path: Path
    ) -> Dict:
        """
        Complete Stage 4 processing: Risk analysis

        Args:
            document_text: Full document text
            entities: Extracted entities
            entity_descriptions: Entity descriptions
            document_name: Name of document
            file_path: Original file path

        Returns:
            Risk assessment report
        """
        risk_report = self.analyze_risks(
            document_text,
            entities,
            entity_descriptions,
            document_name
        )

        # Save risk report
        output_filename = self.file_handler.get_output_filename(
            file_path.name, '_risk_assessment', 'json'
        )
        output_path = Config.RISK_FLAGS_DIR / output_filename
        self.file_handler.save_json(risk_report, output_path)

        # Also save as readable text
        text_filename = self.file_handler.get_output_filename(
            file_path.name, '_risk_assessment', 'txt'
        )
        text_path = Config.RISK_FLAGS_DIR / text_filename

        report_text = self._format_report_text(risk_report)
        self.file_handler.save_text(report_text, text_path)

        print(f"\n{'='*60}")
        print(f"✓ STAGE 4 COMPLETE")
        print(f"{'='*60}\n")

        return risk_report

    def _format_report_text(self, report: Dict) -> str:
        """Format risk report as readable text"""
        doc_risk = report['document_risk_assessment']
        summary = report['entity_risk_summary']

        text = f"""RISK ASSESSMENT REPORT
{'='*60}
Document: {report['document_name']}

DOCUMENT-LEVEL RISK ASSESSMENT
{'-'*60}
Overall Risk Level: {doc_risk['overall_risk_level'].upper()}
Money Laundering Risk: {doc_risk['money_laundering_risk'].upper()}
Sanctions Evasion Risk: {doc_risk['sanctions_evasion_risk'].upper()}

Analysis Summary:
{doc_risk['analysis_summary']}

Red Flags Identified:
"""
        for flag in doc_risk['red_flags']:
            text += f"  • {flag}\n"

        text += f"""
Suspicious Patterns:
"""
        for pattern in doc_risk['suspicious_patterns']:
            text += f"  • {pattern}\n"

        text += f"""

ENTITY RISK SUMMARY
{'-'*60}
Total Flagged Entities: {summary['total_flagged']}
High Risk: {summary['high_risk']}
Medium Risk: {summary['medium_risk']}
Money Laundering Flags: {summary['money_laundering_flags']}
Sanctions Evasion Flags: {summary['sanctions_evasion_flags']}

"""

        if report['flagged_entities']:
            text += f"""FLAGGED ENTITIES DETAILS
{'='*60}
"""
            for entity in report['flagged_entities']:
                text += f"""
{'-'*60}
Entity: {entity['entity_name']}
Type: {entity['entity_type'].upper()}
Risk Level: {entity['risk_level'].upper()}
Confidence: {entity['confidence']:.2f}
Crimes Flagged: {', '.join(entity['crimes_flagged']).replace('_', ' ').title()}

Reasoning:
{entity['reasoning']}

Evidence:
"""
                for evidence in entity['evidence']:
                    text += f"  • {evidence}\n"
        else:
            text += "\nNo entities flagged for criminal activity.\n"

        return text


if __name__ == "__main__":
    # Test the risk analyzer
    import json

    if len(sys.argv) < 4:
        print("Usage: python risk_analyzer.py <text_file> <entities_json> <descriptions_json>")
        sys.exit(1)

    Config.ensure_directories()
    analyzer = RiskAnalyzer()

    text_file = Path(sys.argv[1])
    entities_file = Path(sys.argv[2])
    descriptions_file = Path(sys.argv[3])

    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()

    with open(entities_file, 'r') as f:
        entities = json.load(f)

    with open(descriptions_file, 'r') as f:
        descriptions = json.load(f)

    report = analyzer.process(text, entities, descriptions, text_file.name, text_file)
    print(f"\nRisk report generated with {len(report['flagged_entities'])} flagged entities")
