import pandas as pd
import json
import logging
import os

# Configure logging
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


def process_pharma_sales(file_path):
    logging.info("Starting ETL pipeline: Extraction and transformation")

    # 1. Extraction
    try:
        df = pd.read_csv(file_path)
        logging.info(f"File loaded. Original rows: {len(df)}")
    except FileNotFoundError as e:
        logging.error("Error: File not found.", exc_info=True)
        raise e

    # 2. Structural transformation (unpivot/melt)
    logging.info("Transforming from wide to long format (unpivot)...")

    # Non-medication columns (context variables)
    id_vars = ["datum", "Year", "Month", "Hour", "Weekday Name"]

    # Medication columns to apply melt
    value_vars = ["M01AB", "M01AE", "N02BA", "N02BE", "N05B", "N05C", "R03", "R06"]

    # Apply melt
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=value_vars,
        var_name="codigo_atc",
        value_name="cantidad_vendida",
    )

    # 3. Cleaning and QA in the new format
    audit_log = []
    initial_rows = len(df_long)

    # Rename columns to standardize
    df_long = df_long.rename(
        columns={
            "datum": "fecha",
            "Year": "anio",
            "Month": "mes",
            "Hour": "hora",
            "Weekday Name": "dia_semana",
        }
    )

    # QA: Check for negative sales (anomaly)
    ventas_negativas = len(df_long[df_long["cantidad_vendida"] < 0])
    if ventas_negativas > 0:
        df_long = df_long[df_long["cantidad_vendida"] >= 0]
        audit_log.append(
            f"Removed {ventas_negativas} records with negative sales (possible system error)."
        )

    # QA: Format date correctly
    df_long["fecha"] = pd.to_datetime(df_long["fecha"], errors="coerce")
    fechas_nulas = df_long["fecha"].isnull().sum()
    if fechas_nulas > 0:
        df_long = df_long.dropna(subset=["fecha"])
        audit_log.append(
            f"Removed {fechas_nulas} records with invalid date format."
        )

    final_rows = len(df_long)

    # Report
    logging.info("QA Audit Report Summary:")
    logging.info(f"Final structure: {df_long.shape[0]} rows, {df_long.shape[1]} columns")
    if not audit_log:
        logging.info("Data showed no critical anomalies in this validation")
    for log in audit_log:
        logging.warning(log)
    logging.info(f"Retention percentage: {round((final_rows / initial_rows) * 100, 2)}%")

    return df_long

if __name__ == "__main__":
    input_path = config["paths"]["raw_data"]
    output_path = config["paths"]["clean_data"]
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df_clean = process_pharma_sales(input_path)
    
    # Save the clean file
    df_clean.to_csv(output_path, index=False)
    logging.info(f"Clean data saved to {output_path}")
