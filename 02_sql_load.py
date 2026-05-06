import pandas as pd
import sqlite3


def load_data_to_sqlite(csv_path, db_name, table_name):
    print("Initializing loading process...")
    try:
        # 1. Read the clean CSV from our 'clean zone'
        df_clean = pd.read_csv(csv_path)
        print(f"Clean data read ({len(df_clean)} rows).")

        # 2. Connect to SQLite database (creates the file if it doesn't exist)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # 3. Loading data into the specified table in the SQLite database.
        # We use if_exists='replace' to simulate a "Full Load" process. In a real incremental environment, we would use 'append'.
        print(f"Writing data to the '{table_name}' table...")
        df_clean.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Data successfully inserted into the '{db_name}' database.")

        # 4. Quick verification (Post-load QA)
        # This shows that you don't assume the load worked, but you validate it.
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(
            f"Load QA: The '{table_name}' table has {row_count} stored records."
        )

    except Exception as e:
        # Error handling to prevent the script from crashing silently
        print(f"Critical error during load: {e}")
    finally:
        # 5. Safe closing of the connection
        if "conn" in locals():
            conn.close()
            print("Database connection closed safely.")
            print("--------------------------------------------------")


# Execution block
if __name__ == "__main__":
    csv_source = "data_clean/salesdaily_clean.csv"
    database_name = "pharma_sales.db"
    table_name = "daily_sales"

    load_data_to_sqlite(csv_source, database_name, table_name)
