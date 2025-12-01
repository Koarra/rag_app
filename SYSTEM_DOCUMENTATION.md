# Criminal Entity Detection Testing System - Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Directory Structure](#directory-structure)
4. [Component Details](#component-details)
5. [Comparison Metrics](#comparison-metrics)
6. [Usage Guide](#usage-guide)
7. [Configuration](#configuration)
8. [Interpreting Results](#interpreting-results)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### Purpose
This automated testing system monitors the performance of an LLM-based criminal entity detection script. It ensures consistent accuracy by comparing daily outputs against reference "golden" outputs, tracking two key metrics:
- **Entity Detection Similarity**: How accurately the system identifies entities
- **Crime Classification Similarity**: How accurately crimes are assigned to detected entities

### Key Benefits
- **Early Detection**: Immediately identifies degradation in model performance
- **Historical Tracking**: Maintains logs of all test runs for trend analysis
- **Automated Monitoring**: Runs daily without manual intervention
- **Alerting**: Notifies team when performance drops below acceptable thresholds

### Use Cases
- Detect bugs introduced by code changes
- Monitor impact of prompt modifications
- Track effects of LLM model updates
- Ensure consistent production performance

---

## System Architecture

The system consists of four main components:

```
┌─────────────────┐
│  Test Runner    │ ← Orchestrates daily tests (APScheduler)
│  (test_runner)  │
└────────┬────────┘
         │
         ├─→ ┌──────────────┐
         │   │  Analyzer    │ ← Your existing LLM script
         │   │ (analyzer.py)│
         │   └──────────────┘
         │
         ├─→ ┌──────────────────┐
         │   │ Comparison Engine│ ← Calculates similarity metrics
         │   │ (compare_outputs)│
         │   └──────────────────┘
         │
         └─→ ┌──────────────┐
             │ Alert System │ ← Sends notifications
             │              │
             └──────────────┘
```

### Workflow
1. **Scheduler** triggers test at 2 AM daily
2. **Test Runner** executes analyzer on each test article
3. **Analyzer** generates JSON output with flagged entities
4. **Comparison Engine** calculates similarity metrics
5. **Alert System** notifies team if metrics fall below threshold

---

## Directory Structure

```
project/
├── analyzer.py                      # Your existing LLM entity detection script
├── compare_outputs.py               # Comparison logic and metrics calculation
├── test_runner.py                   # Daily test orchestration
├── config.py                        # Configuration and thresholds
├── quick_test.py                    # Manual testing utility
│
├── data/
│   ├── test_articles/               # Input test documents (5 .docx files)
│   │   ├── money_laundering_scheme.docx
│   │   ├── fraud_network_case.docx
│   │   ├── cybercrime_investigation.docx
│   │   ├── tax_evasion_report.docx
│   │   └── organized_crime_summary.docx
│   │
│   ├── reference_outputs/           # "Golden" reference JSONs (5 files)
│   │   ├── money_laundering_scheme.json
│   │   ├── fraud_network_case.json
│   │   ├── cybercrime_investigation.json
│   │   ├── tax_evasion_report.json
│   │   └── organized_crime_summary.json
│   │
│   └── daily_outputs/               # Generated outputs (timestamped)
│       ├── money_laundering_scheme_2024-12-01T02-00-00.json
│       ├── fraud_network_case_2024-12-01T02-00-00.json
│       └── ...
│
└── logs/
    └── test_results.jsonl           # Historical test results (append-only)
```

---

## Component Details

### 1. analyzer.py (Existing Script)
**Purpose**: Analyzes documents and detects criminal entities

**Usage**:
```bash
python analyzer.py "path/to/article.docx"
```

**Output Format**:
```json
{
  "flagged_entities": [
    {
      "entity_name": "John Smith",
      "entity_type": "person",
      "crimes_flagged": ["money laundering", "fraud"],
      "risk_level": "high",
      "confidence": 0.95,
      "evidence": ["Evidence text..."],
      "reasoning": "Explanation..."
    }
  ]
}
```

**Key Fields**:
- `entity_name`: Name of the flagged entity
- `entity_type`: Type (e.g., "person", "organization")
- `crimes_flagged`: Array of associated crimes
- `risk_level`: Severity assessment ("low", "medium", "high")
- `confidence`: Model confidence score (0.0 to 1.0)
- `evidence`: Supporting evidence from the text
- `reasoning`: Explanation for flagging

---

### 2. compare_outputs.py (Comparison Engine)

**Purpose**: Calculates similarity metrics between reference and current outputs

**Main Function**:
```python
compare_outputs(reference_json, current_json) -> dict
```

**Returns**:
```python
{
    'entity_similarity': 0.75,        # Entity detection Jaccard score
    'crime_similarity': 0.82,         # Crime classification accuracy
    'matched_count': 3,               # Entities found in both
    'missing_count': 1,               # Entities in reference only
    'extra_count': 1,                 # Entities in current only
    'missing_entities': ['name|type'],# List of missed entities
    'extra_entities': ['name|type'],  # List of false positives
    'crime_details': {                # Per-entity crime comparison
        'entity_name|type': {
            'missing_crimes': [...],
            'extra_crimes': [...]
        }
    }
}
```

**Key Functions**:

#### `normalize_entity_key(entity)`
Creates unique identifier for entities by combining name and type (case-insensitive).

```python
# Example:
normalize_entity_key({"entity_name": "John Smith", "entity_type": "person"})
# Returns: "john smith|person"
```

#### `calculate_entity_similarity(reference, current)`
Computes Jaccard similarity for entity detection:

```
Jaccard = |Matched Entities| / |Matched + Missing + Extra|
```

**Example**:
- Reference has: A, B, C
- Current has: A, B, D
- Matched: A, B (2)
- Missing: C (1)
- Extra: D (1)
- Similarity: 2 / (2 + 1 + 1) = 0.50 (50%)

#### `calculate_crime_similarity(reference, current, matched_entities)`
For each matched entity, compares crime arrays using Jaccard similarity, then averages across all entities.

**Example**:
```
Entity "John Smith":
  Reference crimes: ["fraud", "money laundering", "tax evasion"]
  Current crimes: ["fraud", "money laundering"]
  
  Matching: 2
  Total unique: 3
  Similarity: 2/3 = 0.67
  
Average across all matched entities
```

#### `get_crime_details(reference, current, matched_entities)`
Provides detailed breakdown of crime mismatches for debugging.

---

### 3. test_runner.py (Orchestrator)

**Purpose**: Automates daily testing across all test articles

**Main Function**:
```python
run_daily_test()
```

**Process**:
1. Iterates through configured test articles
2. Runs analyzer on each article via subprocess
3. Loads corresponding reference output
4. Saves timestamped current output
5. Performs comparison
6. Aggregates metrics across all articles
7. Logs results to JSONL file
8. Triggers alert if thresholds not met

**Scheduling**:
```python
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()
scheduler.add_job(run_daily_test, 'cron', hour=2, minute=0)
scheduler.start()  # Runs at 2 AM daily
```

**Log Entry Format** (`logs/test_results.jsonl`):
```json
{
  "timestamp": "2024-12-01T02:00:00",
  "avg_entity_similarity": 0.78,
  "avg_crime_similarity": 0.85,
  "threshold": 0.70,
  "passed": true,
  "individual_results": [
    {
      "article": "money_laundering_scheme",
      "entity_similarity": 0.80,
      "crime_similarity": 0.90,
      "details": {...}
    }
  ]
}
```

---

### 4. config.py (Configuration)

**Purpose**: Centralized configuration for test articles and thresholds

```python
# List of test articles (without .docx extension)
TEST_ARTICLES = [
    "money_laundering_scheme",
    "fraud_network_case",
    "cybercrime_investigation",
    "tax_evasion_report",
    "organized_crime_summary"
]

# Similarity threshold (0.0 to 1.0)
SIMILARITY_THRESHOLD = 0.70  # 70%

# Paths
TEST_ARTICLES_DIR = "data/test_articles"
REFERENCE_OUTPUTS_DIR = "data/reference_outputs"
DAILY_OUTPUTS_DIR = "data/daily_outputs"
LOG_FILE = "logs/test_results.jsonl"

# Alert configuration
ALERT_EMAIL = "team@example.com"
ALERT_SLACK_WEBHOOK = "https://hooks.slack.com/..."
```

---

### 5. quick_test.py (Manual Testing)

**Purpose**: Quick validation during development

**Usage**:
```bash
python quick_test.py
```

**Output**:
```
============================================================
COMPARISON RESULTS
============================================================

Entity Detection Similarity: 66.67%
Crime Classification Similarity: 75.00%

Matched Entities: 2
Missing Entities: 1
Extra Entities: 1

Missing: ['maria garcia|person']
Extra: ['robert johnson|person']

Crime Details:
  john smith|person:
    Missing crimes: ['tax evasion']
  abc holdings ltd|organization:
    Extra crimes: ['tax evasion']
============================================================
```

---

## Comparison Metrics

### Metric 1: Entity Detection Similarity

**What it measures**: How well the system identifies the correct entities

**Formula**: Jaccard Index
```
Entity Similarity = Matched / (Matched + Missing + Extra)
```

**Interpretation**:
- **1.0 (100%)**: Perfect match - all entities detected, no false positives
- **0.75 (75%)**: Good - most entities found with few errors
- **0.50 (50%)**: Fair - significant missing or extra entities
- **< 0.50**: Poor - major detection issues

**Example**:
```
Reference entities: John Smith, ABC Corp, Maria Garcia
Current entities: John Smith, ABC Corp, Robert Lee

Matched: 2 (John Smith, ABC Corp)
Missing: 1 (Maria Garcia)
Extra: 1 (Robert Lee)

Similarity = 2 / (2 + 1 + 1) = 0.50 (50%)
```

---

### Metric 2: Crime Classification Similarity

**What it measures**: How accurately crimes are assigned to detected entities

**Formula**: Average Jaccard across matched entities
```
For each matched entity:
  Entity Crime Similarity = Matching Crimes / Total Unique Crimes

Crime Similarity = Average across all matched entities
```

**Interpretation**:
- **1.0 (100%)**: Perfect crime assignment for all entities
- **0.80 (80%)**: Most crimes correctly classified
- **0.60 (60%)**: Moderate accuracy, some misclassifications
- **< 0.50**: Poor crime classification

**Example**:
```
Entity: "John Smith"
  Reference: ["fraud", "money laundering", "tax evasion"]
  Current: ["fraud", "money laundering"]
  Matching: 2
  Total unique: 3
  Similarity: 2/3 = 0.67

Entity: "ABC Corp"
  Reference: ["money laundering"]
  Current: ["money laundering", "tax evasion"]
  Matching: 1
  Total unique: 2
  Similarity: 1/2 = 0.50

Average Crime Similarity = (0.67 + 0.50) / 2 = 0.585 (58.5%)
```

---

### Alert Conditions

An alert is triggered when **EITHER** metric falls below threshold:

```python
if avg_entity_similarity < 0.70 OR avg_crime_similarity < 0.70:
    trigger_alert()
```

**Why both metrics matter**:
- **Entity Detection**: Ensures we're finding the right suspects
- **Crime Classification**: Ensures we're charging them correctly

A system that finds all entities but misclassifies crimes, or correctly classifies crimes but misses entities, is equally problematic.

---

## Usage Guide

### Initial Setup

**1. Install Dependencies**
```bash
pip install apscheduler
```

**2. Create Directory Structure**
```bash
mkdir -p data/test_articles data/reference_outputs data/daily_outputs logs
```

**3. Prepare Test Data**
- Place 5 test documents in `data/test_articles/` (as .docx files)
- Run analyzer manually on each to generate reference outputs
- Review and validate reference outputs
- Place them in `data/reference_outputs/`

**4. Configure Settings**
Edit `config.py` to set:
- Test article names
- Similarity threshold
- Alert recipients

---

### Running Tests

#### Automated Daily Tests
```bash
# Start the scheduler (runs in background)
python test_runner.py
```

This runs tests at 2 AM daily. Use a process manager like `supervisord` or `systemd` for production deployment.

#### Manual Test Run
```bash
# Run tests immediately
python test_runner.py --manual
```

#### Quick Validation
```bash
# Test with just 2 files
python quick_test.py
```

---

### Viewing Results

#### Check Latest Results
```bash
# View last 5 test runs
tail -n 5 logs/test_results.jsonl | jq
```

#### Analyze Trends
```python
import json

with open('logs/test_results.jsonl', 'r') as f:
    results = [json.loads(line) for line in f]

# Get average metrics over last 7 days
recent = results[-7:]
avg_entity = sum(r['avg_entity_similarity'] for r in recent) / len(recent)
avg_crime = sum(r['avg_crime_similarity'] for r in recent) / len(recent)

print(f"7-day average entity detection: {avg_entity:.2%}")
print(f"7-day average crime classification: {avg_crime:.2%}")
```

---

## Configuration

### Adjusting Thresholds

The default threshold is **70%**. Adjust based on your requirements:

```python
# Strict monitoring (fewer false negatives)
SIMILARITY_THRESHOLD = 0.85  # 85%

# Lenient monitoring (only catch major issues)
SIMILARITY_THRESHOLD = 0.60  # 60%
```

**Considerations**:
- **Higher threshold**: More alerts, catches subtle degradation
- **Lower threshold**: Fewer alerts, only catches major problems
- **Recommendation**: Start at 70%, adjust based on false positive rate

---

### Modifying Test Schedule

Change the cron expression in `test_runner.py`:

```python
# Run every 6 hours
scheduler.add_job(run_daily_test, 'cron', hour='*/6')

# Run on weekdays only at 3 AM
scheduler.add_job(run_daily_test, 'cron', day_of_week='mon-fri', hour=3)

# Run every hour during business hours
scheduler.add_job(run_daily_test, 'cron', day_of_week='mon-fri', hour='9-17')
```

---

### Adding New Test Articles

**1. Add the document**
```bash
cp new_case.docx data/test_articles/
```

**2. Generate reference output**
```bash
python analyzer.py "data/test_articles/new_case.docx"
# Review output for accuracy
cp output.json data/reference_outputs/new_case.json
```

**3. Update configuration**
```python
# config.py
TEST_ARTICLES = [
    "money_laundering_scheme",
    "fraud_network_case",
    "cybercrime_investigation",
    "tax_evasion_report",
    "organized_crime_summary",
    "new_case"  # Add here
]
```

---

## Interpreting Results

### Healthy System
```
Entity Detection Similarity: 92%
Crime Classification Similarity: 88%
Matched: 5, Missing: 0, Extra: 0
```
**Interpretation**: System performing well, minimal deviations from reference.

---

### Entity Detection Issue
```
Entity Detection Similarity: 58%
Crime Classification Similarity: 85%
Matched: 3, Missing: 2, Extra: 1
Missing: ['maria garcia|person', 'xyz corp|organization']
```
**Interpretation**: 
- System missing important entities (Maria Garcia, XYZ Corp)
- One false positive detected
- Crime classification still accurate for matched entities
- **Action**: Investigate entity extraction logic

---

### Crime Classification Issue
```
Entity Detection Similarity: 90%
Crime Classification Similarity: 62%
Matched: 5, Missing: 0, Extra: 0

Crime Details:
  john smith|person:
    Missing crimes: ['tax evasion', 'conspiracy']
  abc corp|organization:
    Extra crimes: ['fraud', 'embezzlement']
```
**Interpretation**:
- All entities correctly identified
- Crimes being misclassified or missed
- **Action**: Review crime classification prompts or logic

---

### Systematic Degradation
```
Last 7 days trend:
Day 1: 88% / 85%
Day 2: 86% / 84%
Day 3: 84% / 82%
Day 4: 79% / 80%
Day 5: 75% / 77%
Day 6: 71% / 73%
Day 7: 68% / 70% ← Alert triggered
```
**Interpretation**:
- Gradual performance decline
- Could indicate model drift or environmental changes
- **Action**: Review recent code/prompt changes, check API versions

---

## Troubleshooting

### Issue: "FileNotFoundError: reference output not found"

**Cause**: Missing reference JSON for a test article

**Solution**:
```bash
# Generate missing reference
python analyzer.py "data/test_articles/missing_article.docx"
mv output.json data/reference_outputs/missing_article.json
```

---

### Issue: "All metrics showing 0%"

**Cause**: JSON structure mismatch or parsing error

**Solution**:
1. Validate JSON format:
```bash
python -m json.tool data/reference_outputs/article.json
```
2. Ensure `flagged_entities` key exists
3. Check entity structure matches expected format

---

### Issue: "Constant false alerts"

**Cause**: Threshold too high for natural variance

**Solution**:
1. Analyze typical variance:
```python
# Calculate standard deviation of metrics
import statistics
results = [...]  # Load from logs
entity_scores = [r['avg_entity_similarity'] for r in results]
std_dev = statistics.stdev(entity_scores)
print(f"Standard deviation: {std_dev:.2%}")
```
2. Adjust threshold to: `mean - (2 * std_dev)`

---

### Issue: "Scheduler not running"

**Cause**: Script terminated or not running in background

**Solution**:
```bash
# Use systemd (Linux)
sudo systemctl start entity-testing.service

# Or use screen/tmux
screen -S entity-testing
python test_runner.py
# Detach with Ctrl+A, D

# Or use nohup
nohup python test_runner.py > test_runner.log 2>&1 &
```

---

### Issue: "Memory issues with large files"

**Cause**: Accumulating too many daily outputs

**Solution**: Add cleanup routine
```python
# In test_runner.py, add retention policy
def cleanup_old_outputs(days_to_keep=30):
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    for file in Path('data/daily_outputs').glob('*.json'):
        # Parse timestamp from filename
        # Delete if older than cutoff
```

---

## Best Practices

### 1. Reference Output Quality
- Manually review all reference outputs
- Have multiple team members validate
- Update references when business rules change
- Document why each entity was flagged

### 2. Test Article Selection
- Choose diverse, representative cases
- Include edge cases and difficult scenarios
- Update articles periodically to prevent overfitting
- Balance between simple and complex cases

### 3. Monitoring
- Review logs weekly for trends
- Don't just rely on alerts - check metrics proactively
- Keep notes on why metrics change
- Correlate changes with deployments

### 4. Alert Fatigue
- Start with conservative threshold
- Fine-tune based on false positive rate
- Consider graduated alerts (warning vs critical)
- Add context to alerts (what changed, when)

### 5. Version Control
- Commit reference outputs to git
- Tag versions when updating test suite
- Document changes in CHANGELOG
- Track which code version produced each reference

---

## Maintenance Checklist

### Weekly
- [ ] Review test results for trends
- [ ] Check for systematic issues
- [ ] Validate no false alerts

### Monthly
- [ ] Analyze metric trends
- [ ] Review and update reference outputs if needed
- [ ] Clean up old daily outputs (>30 days)
- [ ] Verify test articles still relevant

### Quarterly
- [ ] Evaluate threshold appropriateness
- [ ] Add new test cases for edge cases found in production
- [ ] Update documentation with lessons learned
- [ ] Performance review of testing system itself

### After Code Changes
- [ ] Run manual test before deploying
- [ ] Monitor first automated run closely
- [ ] Document expected metric changes
- [ ] Update references if business logic changed intentionally

---

## Appendix

### A. JSON Schema

Expected analyzer output structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["flagged_entities"],
  "properties": {
    "flagged_entities": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["entity_name", "entity_type", "crimes_flagged"],
        "properties": {
          "entity_name": {"type": "string"},
          "entity_type": {"type": "string"},
          "crimes_flagged": {
            "type": "array",
            "items": {"type": "string"}
          },
          "risk_level": {"type": "string"},
          "confidence": {"type": "number"},
          "evidence": {
            "type": "array",
            "items": {"type": "string"}
          },
          "reasoning": {"type": "string"}
        }
      }
    }
  }
}
```

### B. Metric Formulas

**Jaccard Similarity**:
```
J(A, B) = |A ∩ B| / |A ∪ B|
        = |intersection| / |union|
        = matched / (matched + missing + extra)
```

**Average Jaccard** (for crime classification):
```
Avg_J = (1/n) * Σ J(A_i, B_i)
where n = number of matched entities
```

### C. File Naming Conventions

**Test Articles**: `{descriptive_name}.docx`
- ✅ `money_laundering_scheme.docx`
- ❌ `test_1.docx`

**Reference Outputs**: `{same_name_as_article}.json`
- ✅ `money_laundering_scheme.json`
- ❌ `money_laundering_scheme_reference.json`

**Daily Outputs**: `{article_name}_{ISO_timestamp}.json`
- ✅ `money_laundering_scheme_2024-12-01T02-00-00.json`
- ❌ `output_20241201.json`

---

## Support

For questions or issues:
1. Check this documentation
2. Review logs in `logs/test_results.jsonl`
3. Run `quick_test.py` for debugging
4. Contact the development team

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Maintained By**: Development Team
