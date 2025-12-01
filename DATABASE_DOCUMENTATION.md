# Database Documentation

## Overview
This Streamlit application uses **dual database storage** (SQLite and DuckDB) to persist document analysis results, track entity changes over time, and enable session management for document processing workflows.

## Databases

### 1. SQLite Database
- **File**: `articledetective_feedback.db`
- **Purpose**: Primary storage with broad compatibility
- **Use case**: General querying and data persistence

### 2. DuckDB Database
- **File**: `articledetective_feedback.duckdb`
- **Purpose**: Analytical queries and history tracking
- **Use case**: Fast aggregations and time-series analysis

Both databases maintain identical schemas and are updated simultaneously to ensure consistency.

## Schema

### Dynamic Entity Tables: `entities_{folder_name}`
Each document processing session creates a table storing entity analysis results. Tables are named dynamically based on the document folder (e.g., `entities_batch_abc123`).

| Column | Type | Description |
|--------|------|-------------|
| `entity` | TEXT | Entity name (person/company) |
| `summary` | TEXT | Description of the entity |
| `money_laundering` | BOOLEAN | Financial crime flag |
| `sanctions_evasion` | BOOLEAN | Financial crime flag |
| `terrorist_financing` | BOOLEAN | Financial crime flag |
| `bribery` | BOOLEAN | Financial crime flag |
| `corruption` | BOOLEAN | Financial crime flag |
| `embezzlement` | BOOLEAN | Financial crime flag |
| `fraud` | BOOLEAN | Financial crime flag |
| `tax_evasion` | BOOLEAN | Financial crime flag |
| `insider_trading` | BOOLEAN | Financial crime flag |
| `market_manipulation` | BOOLEAN | Financial crime flag |
| `ponzi_scheme` | BOOLEAN | Financial crime flag |
| `pyramid_scheme` | BOOLEAN | Financial crime flag |
| `identity_theft` | BOOLEAN | Financial crime flag |
| `cybercrime` | BOOLEAN | Financial crime flag |
| `human_trafficking` | BOOLEAN | Financial crime flag |
| `timestamp` | TIMESTAMP | Record creation time |
| `comments` | TEXT | User feedback/notes |
| `flagged` | BOOLEAN | Overall risk flag |
| `session_id` | TEXT | Processing session identifier |

**Primary Key**: (`entity`, `timestamp`)

## Key Features

### 1. Entity Change Tracking
- Records history of entity risk assessments
- Tracks which financial crimes were flagged over time
- Only saves when data changes (deduplication logic)
- Enables audit trails for compliance

### 2. Session Management (JSON-based)
- Saves/loads document processing sessions via JSON files
- Stores metadata: session name, timestamp, output folder, file names
- Allows users to resume previous analysis work
- Sessions stored in `uploaded_documents/sessions/`

### 3. User Feedback Integration
- Captures user comments for specific entities
- Preserves manual edits to risk flags
- Records which entities users marked as flagged/unflagged

## Typical Workflow

```python
from database_utils import save_to_database, create_dataframe_from_results

# 1. Process documents and generate analysis results
entities_dict = {...}  # Entity names to descriptions
risk_assessment = {...}  # Risk analysis with flagged entities
comments_dict = {...}  # User comments per entity

# 2. Create DataFrame from results
df = create_dataframe_from_results(
    entities_dict, 
    risk_assessment, 
    comments_dict
)

# 3. Save to both databases
success, message = save_to_database(
    df=df,
    table_name="entities_my_document",
    session_id="abc123",
    sqlite_db_path="articledetective_feedback.db",
    duckdb_db_path="articledetective_feedback.duckdb"
)

# 4. Query entity history (DuckDB optimized)
import duckdb
conn = duckdb.connect("articledetective_feedback.duckdb")
history = conn.execute("""
    SELECT * FROM entities_my_document
    WHERE entity = ?
    ORDER BY timestamp DESC
""", ["John Doe"]).fetchdf()
```

## Change Detection Logic
The database only inserts new records when:
- Entity doesn't exist in the table, OR
- Crime flags have changed from last entry, OR
- User comments have been updated

This prevents duplicate entries and maintains a clean change history.

## Benefits
- **Dual Storage**: SQLite for compatibility, DuckDB for analytics
- **Audit Trail**: Complete history of risk assessment changes
- **Feedback Loop**: Integrates user corrections and comments
- **Deduplication**: Smart change detection avoids redundant saves
- **Session Persistence**: Resume analysis work anytime
- **Compliance Ready**: Timestamped records for regulatory review

## File Locations
- **Databases**: `uploaded_documents/articledetective_feedback.{db,duckdb}`
- **Sessions**: `uploaded_documents/sessions/*.json`
- **Documents**: `uploaded_documents/{folder_name}/`
