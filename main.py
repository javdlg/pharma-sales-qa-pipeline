import json
import logging
import os
import extraction_qa
import sql_load

# Configure logging for the main orchestrator
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler()
    ]
)

def run_pipeline():
    logging.info("=" * 50)
    logging.info("STARTING MASTER PIPELINE EXECUTION")
    logging.info("=" * 50)
    
    # 1. Load configuration
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
        logging.info("Configuration loaded successfully.")
    except Exception as e:
        logging.error("Failed to load config.json. Pipeline aborted.", exc_info=True)
        return

    raw_path = config["paths"]["raw_data"]
    clean_path = config["paths"]["clean_data"]
    db_name = config["database"]["db_name"]
    table_name = config["database"]["table_name"]

    # 2. Execute Step 1: Extraction & QA
    logging.info("--- Phase 1: Extraction & QA ---")
    try:
        # Run transformation and QA
        df_clean = extraction_qa.process_pharma_sales(raw_path)
        
        # Save the clean data to the staging/clean area
        os.makedirs(os.path.dirname(clean_path), exist_ok=True)
        df_clean.to_csv(clean_path, index=False)
        logging.info(f"Clean staging file generated at: {clean_path}")
        
    except Exception as e:
        logging.error("Pipeline failed during Extraction & QA Phase. Aborting.", exc_info=True)
        return # Stop execution if Step 1 fails

    # 3. Execute Step 2: SQL Load
    logging.info("--- Phase 2: SQL Database Load ---")
    try:
        sql_load.load_data_to_sqlite(clean_path, db_name, table_name)
    except Exception as e:
        logging.error("Pipeline failed during SQL Loading Phase. Aborting.", exc_info=True)
        return # Stop execution if Step 2 fails

    logging.info("=" * 50)
    logging.info("MASTER PIPELINE COMPLETED SUCCESSFULLY")
    logging.info("=" * 50)

if __name__ == "__main__":
    run_pipeline()
