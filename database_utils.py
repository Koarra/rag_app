"""
Database utilities for saving analysis results to SQLite and DuckDB
"""

import sqlite3
import duckdb
from datetime import datetime
from pathlib import Path
import pandas as pd


# Financial crime categories (from step5)
CRIME_CATEGORIES = [
    "money_laundering",
    "sanctions_evasion",
    "terrorist_financing",
    "bribery",
    "corruption",
    "embezzlement",
    "fraud",
    "tax_evasion",
    "insider_trading",
    "market_manipulation",
    "ponzi_scheme",
    "pyramid_scheme",
    "identity_theft",
    "cybercrime",
    "human_trafficking"
]


def save_to_database(df, table_name, session_id, sqlite_db_path, duckdb_db_path):
    """
    Save entity data to both SQLite and DuckDB databases

    Args:
        df: DataFrame with columns: entity, summary, crime flags (bool), comments, flagged
        table_name: Name of the table to save to
        session_id: Session ID for tracking
        sqlite_db_path: Path to SQLite database
        duckdb_db_path: Path to DuckDB database
    """

    try:
        # Connect to databases
        conn_sqlite = sqlite3.connect(sqlite_db_path)
        conn_duckdb = duckdb.connect(str(duckdb_db_path))

        # Create table schema with crime categories as boolean columns
        crime_columns_sqlite = ", ".join(
            f'"{crime}" BOOLEAN' for crime in CRIME_CATEGORIES
        )
        crime_columns_duckdb = ", ".join(
            f'"{crime}" BOOLEAN' for crime in CRIME_CATEGORIES
        )

        create_table_sqlite = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            entity TEXT,
            summary TEXT,
            {crime_columns_sqlite},
            timestamp TEXT,
            comments TEXT,
            flagged BOOLEAN,
            session_id TEXT,
            PRIMARY KEY(entity, timestamp)
        )
        """

        create_table_duckdb = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            entity TEXT,
            summary TEXT,
            {crime_columns_duckdb},
            timestamp TIMESTAMP,
            comments TEXT,
            flagged BOOLEAN,
            session_id TEXT,
            PRIMARY KEY(entity, timestamp)
        )
        """

        conn_sqlite.execute(create_table_sqlite)
        conn_duckdb.execute(create_table_duckdb)

        # Prepare column names for insert
        column_names = ['entity', 'summary'] + [f'"{crime}"' for crime in CRIME_CATEGORIES] + ['timestamp', 'comments', 'flagged', 'session_id']
        num_columns = len(column_names)

        # Prepare data for insertion
        insert_data = []
        current_timestamp = datetime.now().isoformat()

        for _, row in df.iterrows():
            entity = str(row.get('entity', '')).replace("'", "''")
            summary = str(row.get('summary', '')).replace("'", "''")
            comments = str(row.get('comments', '')).replace("'", "''")
            flagged = bool(row.get('flagged', False))

            # Get crime flags (default to False if not present)
            crime_flags = tuple(
                bool(row.get(crime, False)) for crime in CRIME_CATEGORIES
            )

            # Check if this entity already exists with same data
            query = f"SELECT * FROM {table_name} WHERE entity = ? ORDER BY timestamp DESC LIMIT 1"
            last_entry_sqlite = conn_sqlite.execute(query, (entity,)).fetchone()

            # Only insert if data has changed or doesn't exist
            should_insert = False
            if not last_entry_sqlite:
                should_insert = True
            else:
                # Compare crime flags and comments (skip entity, summary, timestamp, session_id)
                last_crimes = last_entry_sqlite[2:2+len(CRIME_CATEGORIES)]
                last_comments = last_entry_sqlite[-3]
                if last_crimes != crime_flags or last_comments != comments:
                    should_insert = True

            if should_insert:
                data_row = tuple([entity, summary] + list(crime_flags) + [current_timestamp, comments, flagged, session_id])
                insert_data.append(data_row)

        # Insert new rows
        if insert_data:
            placeholders = ', '.join(['?'] * num_columns)
            query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
            conn_sqlite.executemany(query, insert_data)
            conn_duckdb.executemany(query, insert_data)

            conn_sqlite.commit()
            conn_duckdb.commit()

            return True, f"Successfully saved {len(insert_data)} entities to database"
        else:
            return True, "No new changes to save"

    except Exception as e:
        return False, f"Error saving to database: {str(e)}"

    finally:
        conn_sqlite.close()
        conn_duckdb.close()


def create_dataframe_from_results(entities_dict, risk_assessment, comments_dict=None):
    """
    Create a DataFrame from analysis results for database saving

    Args:
        entities_dict: Dict of entity names to descriptions
        risk_assessment: Risk assessment dict with flagged_entities
        comments_dict: Optional dict of entity names to comments

    Returns:
        DataFrame ready for database saving
    """

    # Initialize data structure
    data = {'entity': [], 'summary': [], 'comments': [], 'flagged': []}

    # Add crime category columns
    for crime in CRIME_CATEGORIES:
        data[crime] = []

    # Build a mapping of entities to their crimes
    entity_crimes = {}
    for flagged_entity in risk_assessment.get('flagged_entities', []):
        entity_name = flagged_entity['entity_name']
        crimes = flagged_entity['crimes_flagged']
        entity_crimes[entity_name] = set(crimes)

    # Process each entity
    for entity_name, description in entities_dict.items():
        data['entity'].append(entity_name)
        data['summary'].append(description)
        data['comments'].append(comments_dict.get(entity_name, '') if comments_dict else '')
        data['flagged'].append(entity_name in entity_crimes)

        # Set crime flags
        entity_crime_set = entity_crimes.get(entity_name, set())
        for crime in CRIME_CATEGORIES:
            data[crime].append(crime in entity_crime_set)

    return pd.DataFrame(data)


def get_entity_history(entity_name, table_name, duckdb_db_path):
    """
    Get the history of changes for a specific entity

    Args:
        entity_name: Name of the entity
        table_name: Table name
        duckdb_db_path: Path to DuckDB database

    Returns:
        DataFrame with entity history
    """

    try:
        conn = duckdb.connect(str(duckdb_db_path))
        query = f"""
        SELECT * FROM {table_name}
        WHERE entity = ?
        ORDER BY timestamp DESC
        """
        result = conn.execute(query, (entity_name,)).fetchdf()
        conn.close()
        return result

    except Exception as e:
        print(f"Error fetching entity history: {e}")
        return pd.DataFrame()
