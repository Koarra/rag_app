"""Configuration for KMPI monitoring"""
import os
from pathlib import Path

# Test data location
TEST_DATA_ROOT = Path(os.getenv('RAG_APP_TEST_DATA_PATH', '/home/user/rag_app_test_data'))

# Test articles to check
TEST_ARTICLES = ["article1", "article2", "article3", "article4", "article5"]

# KMPI thresholds
ENTITY_THRESHOLD = 0.85  # 85% (KMPI #1 and #2)
CRIME_THRESHOLD = 0.85   # 85%
ENTITY_THRESHOLD_ALT = 0.83  # 83% (KMPI #5)

# Productivity settings (KMPI #4)
BASELINE_ARTICLES_PER_PERSON = 200
MAX_ARTICLES_PER_PERSON = 400  # 100% increase limit

# Directories
TEST_ARTICLES_DIR = TEST_DATA_ROOT / "test_articles"
REFERENCE_OUTPUTS_DIR = TEST_DATA_ROOT / "reference_outputs"
DAILY_OUTPUTS_DIR = TEST_DATA_ROOT / "daily_outputs"
LOGS_DIR = TEST_DATA_ROOT / "logs"
KMPI_REPORTS_DIR = TEST_DATA_ROOT / "kmpi_reports"
PRODUCTION_METRICS_DIR = TEST_DATA_ROOT / "production_metrics"

# Create directories
for d in [TEST_ARTICLES_DIR, REFERENCE_OUTPUTS_DIR, DAILY_OUTPUTS_DIR, LOGS_DIR, KMPI_REPORTS_DIR, PRODUCTION_METRICS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
