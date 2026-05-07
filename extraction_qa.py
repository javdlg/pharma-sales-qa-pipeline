import pandas as pd
import numpy as np
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

# Master Catalog of allowed ATC codes
ALLOWED_ATC_CODES = ["M01AB", "M01AE", "N02BA", "N02BE", "N05B", "N05C", "R03", "R06"]

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

    # Medication columns to apply melt (all except id_vars)
    value_vars = [col for col in df.columns if col not in id_vars]

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
    rejections = []
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

    # QA: Master Catalog Validation
    invalid_atc_mask = ~df_long["codigo_atc"].isin(ALLOWED_ATC_CODES)
    invalid_atc_rows = df_long[invalid_atc_mask].copy()
    if not invalid_atc_rows.empty:
        invalid_atc_rows["rejection_reason"] = "Invalid ATC Code"
        rejections.append(invalid_atc_rows)
        df_long = df_long[~invalid_atc_mask]
        audit_log.append(f"Removed {len(invalid_atc_rows)} records with invalid ATC codes.")

    # QA: Check for negative sales (anomaly)
    negative_sales_mask = df_long["cantidad_vendida"] < 0
    negative_sales_rows = df_long[negative_sales_mask].copy()
    if not negative_sales_rows.empty:
        negative_sales_rows["rejection_reason"] = "Negative Sales"
        rejections.append(negative_sales_rows)
        df_long = df_long[~negative_sales_mask]
        audit_log.append(f"Removed {len(negative_sales_rows)} records with negative sales (possible system error).")

    # QA: Format date correctly
    df_long["fecha"] = pd.to_datetime(df_long["fecha"], errors="coerce")
    null_dates_mask = df_long["fecha"].isnull()
    null_dates_rows = df_long[null_dates_mask].copy()
    if not null_dates_rows.empty:
        null_dates_rows["rejection_reason"] = "Invalid Date Format"
        rejections.append(null_dates_rows)
        df_long = df_long[~null_dates_mask]
        audit_log.append(f"Removed {len(null_dates_rows)} records with invalid date format.")

    # QA: Outlier Detection (Z-Score method by ATC code)
    # Calculate Z-score for each ATC code group
    # We ignore warnings for cases with 0 std or NaN
    with np.errstate(divide='ignore', invalid='ignore'):
        df_long['z_score'] = df_long.groupby('codigo_atc')['cantidad_vendida'].transform(
            lambda x: (x - x.mean()) / x.std()
        )
    
    # Identify outliers (Z-score > 3 or < -3)
    outliers_mask = df_long['z_score'].abs() > 3
    outliers_rows = df_long[outliers_mask].copy()
    if not outliers_rows.empty:
        outliers_rows["rejection_reason"] = "Statistical Outlier (Z-Score > 3)"
        rejections.append(outliers_rows)
        df_long = df_long[~outliers_mask]
        audit_log.append(f"Removed {len(outliers_rows)} records identified as statistical outliers.")
    
    # Drop the temporary z_score column
    df_long = df_long.drop(columns=['z_score'], errors='ignore')
    if rejections:
        for r in rejections:
            r.drop(columns=['z_score'], inplace=True, errors='ignore')

    # Compile Rejections Report
    if rejections:
        df_rejections = pd.concat(rejections, ignore_index=True)
        qa_report_path = "logs/qa_rejections.csv"
        df_rejections.to_csv(qa_report_path, index=False)
        logging.info(f"QA Rejections Report generated at: {qa_report_path}")

    final_rows = len(df_long)

    # Generate JSON summary
    qa_summary = {
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "total_rejected": sum(len(r) for r in rejections) if rejections else 0,
        "retention_percentage": round((final_rows / initial_rows) * 100, 2) if initial_rows > 0 else 0,
        "audit_log": audit_log
    }
    with open("logs/qa_summary.json", "w") as f:
        json.dump(qa_summary, f, indent=4)
    logging.info("QA Summary JSON generated at: logs/qa_summary.json")

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
