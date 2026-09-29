import sqlite3
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

STRATEGY_DIR = PROCESSED_DIR / "strategy"

DATABASE_DIR = PROJECT_DIR / "data" / "apex_database"

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_FILE = DATABASE_DIR / "apex.db"


# 2. FUNCTION TO LOAD CSV INTO SQL

def load_csv_to_sql(connection, file_path, table_name):

    df = pd.read_csv(file_path)

    df.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False
    )

    print(
        f"Loaded {table_name}: {len(df)} rows"
    )


# 3. CREATE DATABASE

def create_database():

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    print("Creating APEX SQL database...\n")


    # Race summary
    load_csv_to_sql(
        connection,
        PROCESSED_DIR / "race_summary.csv",
        "race_summary"
    )


    # Race results
    load_csv_to_sql(
        connection,
        PROCESSED_DIR / "cleaned_race_results.csv",
        "race_results"
    )


    # Qualifying results
    load_csv_to_sql(
        connection,
        PROCESSED_DIR / "cleaned_qualifying_results.csv",
        "qualifying_results"
    )


    # Machine learning features
    load_csv_to_sql(
        connection,
        PROCESSED_DIR / "driver_race_features.csv",
        "driver_features"
    )


    # Strategy profiles
    load_csv_to_sql(
        connection,
        STRATEGY_DIR / "all_strategy_profiles.csv",
        "strategy_profiles"
    )


    # Individual stints
    load_csv_to_sql(
        connection,
        STRATEGY_DIR / "all_stints.csv",
        "stints"
    )


    # Tyre age and pace
    load_csv_to_sql(
        connection,
        STRATEGY_DIR / "all_tyre_age_pace.csv",
        "tyre_age_pace"
    )


    # Race phase pace
    load_csv_to_sql(
        connection,
        STRATEGY_DIR / "all_phase_pace.csv",
        "phase_pace"
    )


    connection.close()


    print("\nAPEX SQL database created successfully!")

    print(
        f"Database: {DATABASE_FILE}"
    )


# --------------------------------------------------
# 4. RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    create_database()