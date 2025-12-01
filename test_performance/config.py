"""
Configuration for performance testing.
"""

import os
from pathlib import Path

# External test data directory (outside the repository)
# Can be configured via environment variable or uses default
TEST_DATA_ROOT = Path(os.getenv(
    'RAG_APP_TEST_DATA_PATH',
    '/home/user/rag_app_test_data'
))

# Test article names (without extension)
# These should match folders in test_articles/ and files in reference_outputs/
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

# Directories (all stored outside the repository)
TEST_ARTICLES_DIR = TEST_DATA_ROOT / "test_articles"
REFERENCE_OUTPUTS_DIR = TEST_DATA_ROOT / "reference_outputs"
DAILY_OUTPUTS_DIR = TEST_DATA_ROOT / "daily_outputs"
LOGS_DIR = TEST_DATA_ROOT / "logs"

# Create directories if they don't exist
for directory in [TEST_ARTICLES_DIR, REFERENCE_OUTPUTS_DIR, DAILY_OUTPUTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Print configuration on import for verification
print(f"Performance test data location: {TEST_DATA_ROOT}")
print(f"  - Test articles: {TEST_ARTICLES_DIR}")
print(f"  - Reference outputs: {REFERENCE_OUTPUTS_DIR}")
print(f"  - Daily outputs: {DAILY_OUTPUTS_DIR}")
print(f"  - Logs: {LOGS_DIR}")
