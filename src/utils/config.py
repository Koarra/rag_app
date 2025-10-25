"""
Configuration module for document processing pipeline
"""
import os
from pathlib import Path

class Config:
    # API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

    # Model Configuration
    SUMMARIZATION_MODEL = "gpt-4o-mini"  # Fast and cost-effective
    ENTITY_EXTRACTION_MODEL = "gpt-4o"  # More accurate for extraction
    DESCRIPTION_MODEL = "gpt-4o-mini"
    RISK_ANALYSIS_MODEL = "gpt-4o"  # Critical task needs best model

    # Directory Configuration
    BASE_DIR = Path(__file__).parent.parent.parent
    INPUTS_DIR = BASE_DIR / "inputs"
    OUTPUTS_DIR = BASE_DIR / "outputs"

    EXTRACTED_TEXT_DIR = OUTPUTS_DIR / "extracted_text"
    SUMMARIES_DIR = OUTPUTS_DIR / "summaries"
    ENTITIES_DIR = OUTPUTS_DIR / "entities"
    DESCRIPTIONS_DIR = OUTPUTS_DIR / "entity_descriptions"
    RISK_FLAGS_DIR = OUTPUTS_DIR / "risk_flags"

    # Processing Configuration
    MAX_CHUNK_SIZE = 15000  # tokens
    CHUNK_OVERLAP = 500  # tokens
    ENTITY_CONFIDENCE_THRESHOLD = 0.5
    RISK_HIGH_THRESHOLD = 0.7
    RISK_MEDIUM_THRESHOLD = 0.4

    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    @classmethod
    def ensure_directories(cls):
        """Create all necessary directories"""
        for directory in [
            cls.INPUTS_DIR,
            cls.EXTRACTED_TEXT_DIR,
            cls.SUMMARIES_DIR,
            cls.ENTITIES_DIR,
            cls.DESCRIPTIONS_DIR,
            cls.RISK_FLAGS_DIR
        ]:
            directory.mkdir(parents=True, exist_ok=True)
