# Performance Testing for step5_analyze_risks.py

This directory contains automated performance testing for the risk analysis step of the Article Detective application. It compares current LLM outputs against reference outputs to ensure consistent entity detection and crime classification.

## Overview

The performance testing system:
- Runs `step5_analyze_risks.py` on test articles
- Compares outputs against reference "golden" outputs
- Calculates similarity metrics using Jaccard similarity
- Logs results and determines pass/fail based on thresholds
- Saves timestamped outputs for debugging

## Directory Structure

```
test_performance/
├── data/
│   ├── test_articles/          # Test article folders with entity outputs
│   │   ├── article1/
│   │   │   └── outputs/        # Contains entity data files
│   │   ├── article2/
│   │   └── ...
│   ├── reference_outputs/      # Reference "golden" JSON files
│   │   ├── article1.json
│   │   ├── article2.json
│   │   └── ...
│   └── daily_outputs/          # Timestamped current run outputs
├── logs/
│   └── test_results.jsonl     # Append-only test result log
├── compare_outputs.py          # Comparison logic
├── config.py                   # Configuration and thresholds
├── run_test.py                 # Main test runner
└── README.md                   # This file
```

## Setup

### 1. Prepare Test Articles

Place your test articles in `data/test_articles/`. Each article should have the same structure as a processed article:

```
test_articles/article1/outputs/
├── entities.json                           # Or whatever entity files step5 needs
├── dict_unique_grouped_entity_summary.json
└── ... (other files from steps 1-4)
```

### 2. Create Reference Outputs

Run step5 manually on each test article to create reference outputs when you're confident the results are correct:

```bash
# Process article1
python step5_analyze_risks.py test_performance/data/test_articles/article1/outputs

# Copy the generated risk_assessment.json as reference
cp test_performance/data/test_articles/article1/outputs/risk_assessment.json \
   test_performance/data/reference_outputs/article1.json
```

Repeat for all test articles (article2, article3, article4, article5).

### 3. Configure Test Articles

Edit `config.py` to list your test articles:

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
  Saved current output to: data/daily_outputs/article1_2025-12-01T10-30-45.json
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

Results logged to: logs/test_results.jsonl
============================================================
```

## Exit Codes

- **0**: All tests passed (all thresholds met)
- **1**: Tests failed (below threshold) or no articles processed

## Configuration

Edit `config.py` to adjust:

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
Ensure test articles exist in `data/test_articles/article_name/outputs/`

### "Reference not found" Error
Create reference outputs by running step5 manually and copying the `risk_assessment.json` file

### Low Similarity Scores
- Check if LLM prompts have changed
- Review the `daily_outputs/` folder to see what's different
- Use crime_details to see specific discrepancies
- Consider updating reference outputs if changes are intentional

## Integration with CI/CD

Add to your CI pipeline:

```yaml
- name: Run Performance Tests
  run: python test_performance/run_test.py
```

Tests will fail (exit code 1) if similarity drops below thresholds, preventing regressions.

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
