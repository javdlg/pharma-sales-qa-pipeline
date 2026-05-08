# pyrefly: ignore [missing-import]
import pytest
import pandas as pd
import os
from extraction_qa import process_pharma_sales, ALLOWED_ATC_CODES

@pytest.fixture
def sample_sales_data(tmp_path):
    """Fixture to create a temporary CSV with known clean and corrupted data."""
    # Create 20 normal rows + 1 row with an invalid date
    dates = [f"2023-01-{i:02d}" for i in range(1, 21)] + ["invalid_date"]
    
    data = {
        "datum": dates,
        "Year": [2023] * 21,
        "Month": [1] * 21,
        "Hour": [12] * 21,
        "Weekday Name": ["Monday"] * 21,
        # M01AB: 19 normal values, 1 negative value, 1 normal value
        "M01AB": [10] * 19 + [-5, 10],  
        # N02BA: 19 normal values, 1 massive outlier, 1 normal value
        "N02BA": [5] * 19 + [5000, 5],     
        # INVALID_ATC: An ATC code not in the master catalog
        "INVALID_ATC": [1] * 21  
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_sales.csv"
    df.to_csv(file_path, index=False)
    
    return str(file_path)

def test_process_pharma_sales_qa_validations(sample_sales_data):
    """Test that the ETL pipeline correctly filters out anomalies."""
    df_clean = process_pharma_sales(sample_sales_data)
    
    # 1. Test unpivot (Wide to Long)
    assert "codigo_atc" in df_clean.columns
    assert "cantidad_vendida" in df_clean.columns
    
    # 2. Test Master Catalog Validation
    assert "INVALID_ATC" not in df_clean["codigo_atc"].values
    
    # 3. Test Negative Sales removal
    assert len(df_clean[df_clean["cantidad_vendida"] < 0]) == 0
    
    # 4. Test Invalid Date removal
    assert pd.isna(df_clean["fecha"]).sum() == 0
    
    # 5. Test Outlier removal (Z-score > 3)
    # The value 5000 should be removed
    assert df_clean[(df_clean["codigo_atc"] == "N02BA") & (df_clean["cantidad_vendida"] == 5000)].empty

def test_rejections_report_generation(sample_sales_data):
    """Test that the pipeline generates the QA reports."""
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Run the pipeline to generate logs
    process_pharma_sales(sample_sales_data)
    
    # Check if files were created
    assert os.path.exists("logs/qa_summary.json")
    assert os.path.exists("logs/qa_rejections.csv")
    
    # Validate rejections file content
    rejections_df = pd.read_csv("logs/qa_rejections.csv")
    rejection_reasons = rejections_df["rejection_reason"].unique()
    
    assert "Invalid ATC Code" in rejection_reasons
    assert "Negative Sales" in rejection_reasons
    assert "Invalid Date Format" in rejection_reasons
    assert "Statistical Outlier (Z-Score > 3)" in rejection_reasons
