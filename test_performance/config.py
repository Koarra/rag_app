"""
Configuration for performance testing.
"""

from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Test article names (without extension)
# These should match files in data/test_articles/ and data/reference_outputs/
TEST_ARTICLES = [
    "article1",
    "article2",
    "article3",
    "article4",
    "article5"
]

# Similarity thresholds
ENTITY_SIMILARITY_THRESHOLD = 0.80  # 80% entity match required
CRIME_SIMILARITY_THRESHOLD = 0.75   # 75% crime match required

# Combined threshold (average of both)
SIMILARITY_THRESHOLD = 0.77

# Directories
TEST_ARTICLES_DIR = BASE_DIR / "data" / "test_articles"
REFERENCE_OUTPUTS_DIR = BASE_DIR / "data" / "reference_outputs"
DAILY_OUTPUTS_DIR = BASE_DIR / "data" / "daily_outputs"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [TEST_ARTICLES_DIR, REFERENCE_OUTPUTS_DIR, DAILY_OUTPUTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
