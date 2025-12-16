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
3. **Interactive Review** (Streamlit UI - Activities Table):
   - User views the Activities Table with flagged criminal entities
   - User can edit the table: modify crime flags, change summaries, unflag entities
   - Changes are saved to session state (`st.session_state.edited_activities_df`)
   - These edits persist during the session but are not yet in the database
4. **Database Storage** (Streamlit UI - Save to Database section):
   - User can add comments to specific entities
   - When "Save to Database" is clicked, data is saved to both SQLite and DuckDB
   - Each save creates a new timestamped record for changed entities
5. **Query & Analysis**: Users can query DuckDB for historical analysis and trends

## User Feedback Loop

### Overview

The application provides an interactive feedback loop where users can review and correct the AI's entity flagging decisions. This human-in-the-loop approach ensures accuracy and allows tracking of AI performance over time.

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1-4: Document Processing                                   │
│ └─> JSON files created (entities, summaries, relationships)     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: AI Risk Analysis                                        │
│ └─> risk_assessment.json (15 crime categories flagged)          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ Streamlit UI: Activities Table (Interactive Review)             │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ [View Mode] Display flagged entities                      │ │
│  │   ├─ Entity Name | Summary | Crime Flags | Flagged       │ │
│  │   └─ Only shows flagged entities, active crime columns   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         │ User clicks "Edit Table"               │
│                         ▼                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ [Edit Mode] Modify any cell                               │ │
│  │   ├─ Toggle crime checkboxes                             │ │
│  │   ├─ Unflag false positives                              │ │
│  │   ├─ Edit summaries                                      │ │
│  │   └─ Add comments                                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         │ User clicks "Save Changes"             │
│                         ▼                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Session State Updated                                     │ │
│  │   └─> st.session_state.edited_activities_df              │ │
│  │   └─> Changes persist during session                     │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ User navigates to "Save to Database"
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ Database Persistence Section                                    │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 1. Add optional comments to entities                      │ │
│  │ 2. Click "Save to Database"                               │ │
│  │ 3. save_to_database() function:                           │ │
│  │    ├─ Creates DataFrame from current data + comments     │ │
│  │    ├─ Checks for changes vs last DB entry                │ │
│  │    ├─ Inserts new timestamped rows (if changed)          │ │
│  │    └─ Saves to SQLite + DuckDB                           │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ Databases (Dual Storage)                                        │
│  ├─ SQLite: entities.db (ACID, reliable, easy backups)         │
│  └─ DuckDB: entities.duckdb (analytics, time-series queries)   │
│                                                                  │
│  Each entity row contains:                                      │
│    ├─ entity, summary, 15 crime flags, timestamp               │
│    ├─ comments, flagged status, session_id                     │
│    └─ PRIMARY KEY (entity, timestamp) for version history      │
└─────────────────────────────────────────────────────────────────┘
```

### How Table Editing Works

#### 1. Initial Display
- After step5 completes, the **Activities Table** shows all entities flagged by the AI
- Each row shows: Entity name, Summary, Crime flags (checkboxes), Comments, and Flagged status
- Only columns with at least one flagged crime are displayed

#### 2. Edit Mode
Users can switch to Edit Mode by clicking **✏️ Edit Table**:
- All cells become editable (except Entity name which is read-only)
- Users can:
  - **Toggle crime flags**: Check/uncheck any of the 15 crime categories
  - **Unflag entities**: Uncheck the "Flagged" column to remove false positives
  - **Edit summaries**: Modify entity descriptions
  - **Add comments**: Add notes or reasoning for changes

#### 3. Save Changes
When **💾 Save Changes** is clicked:
- Edits are saved to Streamlit session state (`st.session_state.edited_activities_df`)
- Changes persist during the current session
- The table view updates to reflect modifications
- Unflagged entities disappear from the table (filter: `Flagged == True`)
- A success toast notification appears

#### 4. Database Persistence
To save edits permanently to the database:
- Go to the **"Save Results to Database"** section
- Optionally add comments to specific entities
- Click **💾 Save to Database**
- This triggers `save_to_database()` which:
  - Creates a DataFrame with current entity data and crime flags
  - Compares against the last database entry for each entity
  - Only inserts new rows if crime flags or comments have changed
  - Saves to both SQLite (ACID compliance) and DuckDB (analytics)
  - Creates timestamped records for audit trail

#### 5. Version History
Each database save creates a new timestamped record:
```sql
-- Example: Entity history over time
SELECT entity, timestamp, money_laundering, fraud, comments
FROM entities
WHERE entity = 'Acme Corp'
ORDER BY timestamp DESC;
```

This allows users to:
- Track how entity classifications change over time
- See who made changes (via session_id)
- Audit AI decisions vs human corrections
- Analyze patterns in false positives/negatives

### Key Benefits of the Feedback Loop

1. **Human-in-the-Loop**: AI makes initial flagging, humans review and correct
2. **Iterative Improvement**: Track AI accuracy over time via version history
3. **Audit Trail**: Complete history of all changes with timestamps
4. **Flexible Editing**: Change crime flags, summaries, comments all in one interface
5. **Session Persistence**: Edits persist during work session before database save
6. **Dual Storage**: Both ACID-compliant (SQLite) and analytics-optimized (DuckDB) storage

### Practical Example: Correcting AI Decisions

**Scenario**: AI flagged "ABC Consulting" for money laundering, but analyst determines it's a false positive.

**Step-by-step correction:**

1. **View the flagged entity** in Activities Table:
   ```
   Entity: ABC Consulting
   Summary: Professional services firm based in Dubai
   Money Laundering: ✅ (checked)
   Fraud: ❌
   Flagged: ✅
   ```

2. **Click "Edit Table"** to enter edit mode

3. **Make corrections**:
   - Uncheck "Money Laundering" box
   - Uncheck "Flagged" box (to remove from flagged list)
   - Add comment: "False positive - legitimate consulting firm"

4. **Click "Save Changes"** - entity disappears from Activities Table (no longer flagged)

5. **Navigate to "Save to Database"** section

6. **Click "Save to Database"** - changes are now permanently stored with timestamp

7. **Query history** to see the correction:
   ```sql
   SELECT entity, timestamp, money_laundering, flagged, comments
   FROM entities
   WHERE entity = 'ABC Consulting'
   ORDER BY timestamp DESC;

   -- Result:
   -- Row 1: 2025-12-01 10:30 | FALSE | FALSE | "False positive - legitimate consulting firm"
   -- Row 2: 2025-12-01 10:15 | TRUE  | TRUE  | ""  (original AI decision)
   ```

### Use Cases for Version History

**1. Track AI Accuracy Over Time**
```sql
-- Count false positives by crime type per session
SELECT
    session_id,
    SUM(CASE WHEN money_laundering = FALSE AND comments LIKE '%false positive%' THEN 1 ELSE 0 END) as ml_false_positives,
    SUM(CASE WHEN fraud = FALSE AND comments LIKE '%false positive%' THEN 1 ELSE 0 END) as fraud_false_positives
FROM entities
GROUP BY session_id;
```

**2. Audit Analyst Corrections**
```sql
-- Find all entities modified after initial flagging
SELECT entity, COUNT(*) as revision_count
FROM entities
GROUP BY entity
HAVING COUNT(*) > 1
ORDER BY revision_count DESC;
```

**3. Generate Training Data for Model Improvement**
```sql
-- Export corrected entities to retrain AI model
SELECT entity, summary, money_laundering, fraud, terrorist_financing, comments
FROM entities
WHERE timestamp = (SELECT MAX(timestamp) FROM entities e2 WHERE e2.entity = entities.entity)
  AND comments != ''
```

**4. Compliance Reporting**
```sql
-- Generate report of all flagged entities with final status
SELECT
    entity,
    summary,
    money_laundering OR fraud OR terrorist_financing as has_crime_flag,
    comments,
    MAX(timestamp) as last_updated
FROM entities
GROUP BY entity
HAVING has_crime_flag = TRUE
```

### Best Practices for Using the Feedback Loop

1. **Review All Flagged Entities**: Don't skip reviewing - AI makes mistakes
2. **Add Meaningful Comments**: Explain why you changed a flag (helps future analysis)
3. **Save to Database Regularly**: Don't lose work - save after each review session
4. **Use Session Management**: Save sessions with descriptive names for later reference
5. **Query History Periodically**: Use DuckDB to analyze patterns and improve AI prompts
6. **Export for Retraining**: Use corrected data to fine-tune the LLM for better accuracy
7. **Reset Only When Needed**: "Reset Table" discards all edits - use sparingly
8. **Filter Columns**: Use the column selector to focus on relevant crime categories

### Technical Implementation Details

**Session State Management** (streamlit_app.py:575-650):
- `st.session_state.edited_activities_df`: Stores current table state
- `st.session_state.edit_mode_table`: Toggle between view/edit mode
- `st.session_state.temp_edited_df`: Temporary storage during editing
- `st.session_state.entity_comments`: User-added comments per entity

**Database Save Logic** (database_utils.py:save_to_database):
```python
# Change detection algorithm
for each entity:
    1. Query last entry from database
    2. Compare crime flags and comments
    3. If changed → insert new timestamped row
    4. If unchanged → skip (no duplicate)
```

**Why Dual Databases?**
- **SQLite**: ACID compliance ensures data integrity, simple backups, universally compatible
- **DuckDB**: Columnar storage for fast analytics, native Parquet export, optimized for OLAP queries

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

## Visualizing Performance Trends with Elbow Plots

### What are Elbow Plots?

Elbow plots visualize how performance metrics evolve over time, helping you identify:
- **Performance trends**: Are metrics improving or degrading?
- **Elbow points**: Significant changes where performance sharply improved or degraded
- **Threshold violations**: When metrics fall below acceptance thresholds
- **Per-article patterns**: How individual articles perform over time

### Generating Elbow Plots

After running multiple performance tests, generate the visualization:

```bash
# Generate plot (saved to daily_outputs/performance_plot.png)
python test_performance/plot_elbow.py
```

The plot shows:
- Entity and crime similarity in two subplots
- Metric values over time with connecting lines
- Red dashed threshold lines showing pass/fail boundaries
- Grid for easy reading of values

### Reading the Plot

**What to look for:**
- **Above red line**: Performance is passing
- **Below red line**: Performance is failing
- **Sudden drops**: May indicate prompt changes, model updates, or LLM API changes
- **Gradual trends**: Shows whether performance is improving or degrading over time
- **Elbow points**: Sharp changes in the trend line

### Example Use Cases

**Track performance over time:**
```bash
# Run tests regularly
python test_performance/run_test.py

# Generate plot to see trends
python test_performance/plot_elbow.py
```

### Creating Sample Data for Testing

To test the elbow plot functionality without running actual tests:

```bash
# Generate 15 sample test runs with realistic performance variations
python test_performance/create_sample_data.py
```

This creates sample data showing:
- Good performance (days 1-5)
- Performance degradation (days 6-10)
- Recovery (days 11-15)

### Dependencies

Elbow plots require additional Python packages:

```bash
pip install matplotlib numpy
```

These are included in `requirements.txt` for the project.

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

### `plot_elbow.py`
Simple script that:
- Reads test results from logs/test_results.jsonl
- Creates two subplots showing entity and crime similarity over time
- Saves plot to daily_outputs/performance_plot.png

### `create_sample_data.py`
Generates 15 sample test runs with realistic performance patterns:
- Good performance → drop → recovery
- Useful for testing and demonstration
