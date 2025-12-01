# Performance Testing for step5_analyze_risks.py

This directory contains automated performance testing for the risk analysis step of the Article Detective application. It compares current LLM outputs against reference outputs to ensure consistent entity detection and crime classification.

## Overview

The performance testing system:
- Runs `step5_analyze_risks.py` on test articles
- Compares outputs against reference "golden" outputs
- Calculates similarity metrics using Jaccard similarity
- Logs results and determines pass/fail based on thresholds
- Saves timestamped outputs for debugging
- **Stores all test data outside the repository** to keep the codebase clean

## Database Architecture

### Main Application Database Usage

The Article Detective application uses **dual database storage** for entity analysis results:

#### SQLite Database
- **Purpose**: Primary relational database for storing entity analysis results
- **File**: `entities.db` (stored in session folder)
- **Schema**:
  ```sql
  CREATE TABLE entities (
      entity TEXT,                    -- Entity name
      summary TEXT,                   -- Entity description
      money_laundering BOOLEAN,       -- Crime flag
      sanctions_evasion BOOLEAN,      -- Crime flag
      terrorist_financing BOOLEAN,    -- Crime flag
      bribery BOOLEAN,                -- Crime flag
      corruption BOOLEAN,             -- Crime flag
      embezzlement BOOLEAN,           -- Crime flag
      fraud BOOLEAN,                  -- Crime flag
      tax_evasion BOOLEAN,            -- Crime flag
      insider_trading BOOLEAN,        -- Crime flag
      market_manipulation BOOLEAN,    -- Crime flag
      ponzi_scheme BOOLEAN,           -- Crime flag
      pyramid_scheme BOOLEAN,         -- Crime flag
      identity_theft BOOLEAN,         -- Crime flag
      cybercrime BOOLEAN,             -- Crime flag
      human_trafficking BOOLEAN,      -- Crime flag
      timestamp TEXT,                 -- Record creation time
      comments TEXT,                  -- User notes
      flagged BOOLEAN,                -- Overall flag status
      session_id TEXT,                -- Session identifier
      PRIMARY KEY(entity, timestamp)  -- Composite key
  )
  ```

#### DuckDB Database
- **Purpose**: Analytical database optimized for querying and history tracking
- **File**: `entities.duckdb` (stored in session folder)
- **Schema**: Same as SQLite, but with `TIMESTAMP` type for timestamp field
- **Use Cases**:
  - Fast analytical queries across large datasets
  - Time-series analysis of entity changes
  - Export to Parquet/CSV for data science workflows

### Key Features

1. **Version History**: Each entity update creates a new row with timestamp, allowing full audit trail
2. **Change Detection**: Only inserts new rows when crime flags or comments change
3. **Session Tracking**: Links all entities to a session_id for batch operations
4. **Dual Storage Benefits**:
   - SQLite: ACID compliance, reliable storage, easy backups
   - DuckDB: Fast analytics, columnar storage, better for large-scale queries

### Database Functions (database_utils.py)

- `save_to_database()`: Saves entity DataFrame to both SQLite and DuckDB
- `create_dataframe_from_results()`: Converts JSON analysis results to database-ready DataFrame
- `get_entity_history()`: Retrieves complete change history for an entity

### Data Flow

1. **Document Processing** (steps 1-4): JSON files are created
2. **Risk Analysis** (step5): `risk_assessment.json` is created with flagged entities
3. **Database Storage** (Streamlit UI):
   - User reviews the Activities Table
   - When "Save Changes" is clicked, data is saved to both SQLite and DuckDB
   - Each save creates a new timestamped record for changed entities
4. **Query & Analysis**: Users can query DuckDB for historical analysis and trends

### Performance Testing Data Storage

**Note:** The performance testing framework itself does **NOT** use SQL databases. It stores data in simple file formats:

- **Test articles**: File-based (original documents + JSON outputs from steps 1-4)
- **Reference outputs**: JSON files (`article_name.json`)
- **Daily outputs**: JSON files with timestamps
- **Test logs**: JSONL (JSON Lines) format for append-only logging

This design keeps performance testing simple, portable, and easy to version control without database dependencies.

## Directory Structure

**Repository structure (code only):**
```
test_performance/
├── compare_outputs.py          # Comparison logic
├── config.py                   # Configuration and thresholds
├── run_test.py                 # Main test runner
├── __init__.py                 # Package initialization
└── README.md                   # This file
```

**External test data structure (default: `/home/user/rag_app_test_data/`):**
```
rag_app_test_data/              # Outside repository
├── test_articles/              # Test article folders with entity outputs
│   ├── article1/
│   │   └── outputs/            # Contains entity data files
│   ├── article2/
│   └── ...
├── reference_outputs/          # Reference "golden" JSON files
│   ├── article1.json
│   ├── article2.json
│   └── ...
├── daily_outputs/              # Timestamped current run outputs
│   └── article1_2025-12-01T10-30-45.json
└── logs/
    └── test_results.jsonl      # Append-only test result log
```

**Note:** The test data location can be customized via the `RAG_APP_TEST_DATA_PATH` environment variable.

## Setup

### 1. Configure Test Data Location (Optional)

By default, test data is stored in `/home/user/rag_app_test_data/`. To use a different location:

```bash
export RAG_APP_TEST_DATA_PATH="/your/custom/path"
```

Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### 2. Prepare Test Articles

Place your test articles in the test data directory. Each article should have the same structure as a processed article:

```
# Default location: /home/user/rag_app_test_data/test_articles/
test_articles/article1/outputs/
├── entities.json                           # Or whatever entity files step5 needs
├── dict_unique_grouped_entity_summary.json
└── ... (other files from steps 1-4)
```

The directories will be created automatically when you run the tests for the first time.

### 3. Create Reference Outputs

Run step5 manually on each test article to create reference outputs when you're confident the results are correct:

```bash
# Set the test data path (if using custom location)
export RAG_APP_TEST_DATA_PATH="/your/custom/path"

# Process article1
python step5_analyze_risks.py /home/user/rag_app_test_data/test_articles/article1/outputs

# Copy the generated risk_assessment.json as reference
cp /home/user/rag_app_test_data/test_articles/article1/outputs/risk_assessment.json \
   /home/user/rag_app_test_data/reference_outputs/article1.json
```

Repeat for all test articles (article2, article3, article4, article5).

### 4. Configure Test Articles

Edit `test_performance/config.py` to list your test articles:

```python
TEST_ARTICLES = [
    "article1",
    "article2",
    "article3",
    "article4",
    "article5"
]
```

## Running Tests

### Run All Tests

```bash
python test_performance/run_test.py
```

### Quiet Mode (Less Output)

```bash
python test_performance/run_test.py --quiet
```

## Metrics

### Entity Detection Similarity
- Compares which entities were detected (entity name + entity type)
- Uses Jaccard similarity: `|intersection| / |union|`
- Threshold: **80%** (configurable in `config.py`)

### Crime Classification Similarity
- For matched entities, compares which crimes were flagged
- Uses Jaccard similarity on crime sets
- Threshold: **75%** (configurable in `config.py`)

### Output Format

For each article:
```
Processing article1...
  Running step5 for article1...
  Saved current output to: /home/user/rag_app_test_data/daily_outputs/article1_2025-12-01T10-30-45.json
  ✓ Entity similarity: 85.00%
  ✓ Crime similarity: 90.00%
    - Matched entities: 17
    - Missing entities: 2
    - Extra entities: 1
    - Crime discrepancies: 3 entities
```

Aggregate summary:
```
============================================================
Test Summary
============================================================
Articles tested: 5
Average entity similarity: 88.40% (threshold: 80%)
Average crime similarity: 85.20% (threshold: 75%)

✅ TEST PASSED - All thresholds met!

Results logged to: /home/user/rag_app_test_data/logs/test_results.jsonl
============================================================
```

## Exit Codes

- **0**: All tests passed (all thresholds met)
- **1**: Tests failed (below threshold) or no articles processed

## Configuration

### Test Data Location

The test data location is configured via environment variable or uses the default:

```python
# In config.py
TEST_DATA_ROOT = Path(os.getenv(
    'RAG_APP_TEST_DATA_PATH',
    '/home/user/rag_app_test_data'  # Default
))
```

To use a custom location:
```bash
export RAG_APP_TEST_DATA_PATH="/path/to/your/test/data"
```

### Similarity Thresholds

Edit `test_performance/config.py` to adjust thresholds:

```python
# Similarity thresholds
ENTITY_SIMILARITY_THRESHOLD = 0.80  # 80%
CRIME_SIMILARITY_THRESHOLD = 0.75   # 75%

# Test articles
TEST_ARTICLES = ["article1", "article2", ...]
```

## Interpreting Results

### Entity Metrics
- **matched_count**: Entities found in both reference and current
- **missing_count**: Entities in reference but not in current (false negatives)
- **extra_count**: Entities in current but not in reference (false positives)

### Crime Details
Shows entities where crime classifications differ:
```json
{
  "entity_name": "John Doe",
  "expected_crimes": ["Money_Laundering", "Tax_Evasion"],
  "detected_crimes": ["Money_Laundering"],
  "missing_crimes": ["Tax_Evasion"],
  "extra_crimes": []
}
```

## Log Format

Results are logged to `logs/test_results.jsonl` (one JSON object per line):

```json
{
  "timestamp": "2025-12-01T10:30:45",
  "test_config": {
    "entity_threshold": 0.8,
    "crime_threshold": 0.75,
    "articles_tested": 5
  },
  "aggregate_metrics": {
    "avg_entity_similarity": 0.884,
    "avg_crime_similarity": 0.852,
    "entity_passed": true,
    "crime_passed": true,
    "overall_passed": true
  },
  "individual_results": [...]
}
```

## Troubleshooting

### "Folder not found" Error
Ensure test articles exist in the test data directory:
```bash
# Default location
ls /home/user/rag_app_test_data/test_articles/article1/outputs/

# Or check your custom location
echo $RAG_APP_TEST_DATA_PATH
ls $RAG_APP_TEST_DATA_PATH/test_articles/article1/outputs/
```

### "Reference not found" Error
Create reference outputs by running step5 manually and copying the `risk_assessment.json` file to the reference_outputs directory. Make sure the environment variable is set if using a custom location.

### Path Configuration Issues
When you run the test, it will print the configured paths:
```
Performance test data location: /home/user/rag_app_test_data
  - Test articles: /home/user/rag_app_test_data/test_articles
  - Reference outputs: /home/user/rag_app_test_data/reference_outputs
  - Daily outputs: /home/user/rag_app_test_data/daily_outputs
  - Logs: /home/user/rag_app_test_data/logs
```
Verify these paths are correct.

### Low Similarity Scores
- Check if LLM prompts have changed
- Review the `daily_outputs/` folder to see what's different
- Use crime_details to see specific discrepancies
- Consider updating reference outputs if changes are intentional

## Integration with CI/CD

Add to your CI pipeline:

```yaml
- name: Run Performance Tests
  env:
    RAG_APP_TEST_DATA_PATH: /path/to/test/data  # Set your test data location
  run: python test_performance/run_test.py
```

Tests will fail (exit code 1) if similarity drops below thresholds, preventing regressions.

**Note:** Make sure your CI environment has access to the test data directory, or configure it to use a CI-specific location.

## Files Description

### `compare_outputs.py`
Contains comparison logic:
- `normalize_entity_key()`: Creates unique entity identifiers
- `calculate_entity_similarity()`: Jaccard similarity for entity sets
- `calculate_crime_similarity()`: Average Jaccard for crime classifications
- `compare_outputs()`: Main comparison function

### `config.py`
Configuration settings:
- Test article names
- Similarity thresholds
- Directory paths

### `run_test.py`
Main test runner:
- Executes step5 for each article
- Loads reference outputs
- Compares and calculates metrics
- Logs results
- Reports pass/fail
