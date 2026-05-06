import pandas as pd
import sqlite3
import json
import logging
import os

# Configurar logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler()
    ]
)

# Load configuration
with open("config.json", "r") as file:
    config = json.load(file)


def load_data_to_sqlite(csv_path, db_name, table_name):
    logging.info("Initializing loading process...")
    try:
        # 1. Read the clean CSV from our 'clean zone'
        df_clean = pd.read_csv(csv_path)
        logging.info(f"Clean data read ({len(df_clean)} rows).")

        # 2. Connect to SQLite database (creates the file if it doesn't exist)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # 3. Loading data into the specified table in the SQLite database.
        # We use if_exists='replace' to simulate a "Full Load" process. In a real incremental environment, we would use 'append'.
        logging.info(f"Writing data to the '{table_name}' table...")
        df_clean.to_sql(table_name, conn, if_exists="replace", index=False)
        logging.info(f"Data successfully inserted into the '{db_name}' database.")

        # 4. Quick verification (Post-load QA)
        # This shows that you don't assume the load worked, but you validate it.
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        logging.info(
            f"Load QA: The '{table_name}' table has {row_count} stored records."
        )

    except Exception as e:
        # Error handling to prevent the script from crashing silently
        logging.error(f"Critical error during load: {e}", exc_info=True)
    finally:
        # 5. Safe closing of the connection
        if "conn" in locals():
            conn.close()
            logging.info("Database connection closed safely.")
            logging.info("-" * 50)


# Execution block
if __name__ == "__main__":
    csv_source = config["paths"]["clean_data"]
    database_name = config["database"]["db_name"]
    table_name = config["database"]["table_name"]

    load_data_to_sqlite(csv_source, database_name, table_name)
