# Pharma Sales Data QA & Analytics Pipeline

## 📌 Project Overview
This project demonstrates an end-to-end Data Analytics and Quality Assurance (QA) pipeline for pharmaceutical sales data. It focuses on extracting raw transactional data, applying strict business rules for data cleansing, transforming structures for relational databases, and ensuring high data reliability.

## 🏢 Business Case & Problem Statement

**The Scenario:**
A regional pharmaceutical distribution network receives daily sales data from dozens of independent pharmacy franchises (Points of Sale).

**The Problem (The "Pain Point"):**
The Business Intelligence (BI) and Analytics teams are spending up to 80% of their time manually cleaning data. Their downstream dashboards frequently break or show inaccurate metrics due to:
- **"Garbage In":** POS system glitches sending negative sales figures or invalid date formats.
- **Compliance Risks:** Franchises occasionally logging non-approved or discontinued drugs (ATC codes not in the master catalog).
- **Manual Entry Errors:** "Fat-finger" errors creating massive statistical outliers (e.g., ringing up 1,000 units instead of 10) which drastically skew demand forecasting.
- **Silent Failures:** When basic ETL pipelines simply drop bad rows to keep running, the Operations team never learns *why* data is missing, leading to untracked revenue loss.

**The Solution:**
This automated QA pipeline acts as a "firewall" between raw franchise data and the analytical data warehouse. It standardizes the data structure (Wide to Long format) and rigorously applies business rules and statistical outlier detection (Z-Score). Most importantly, instead of silently dropping bad data, it generates actionable **Rejection Reports**. This shifts the paradigm from "manual data fixing" by the BI team to "root cause investigation" by the Operations team, ensuring executive dashboards are always built on highly reliable data.

## 🎯 Objectives
- **Data Quality (QA):** Implement automated checks for duplicates, negative values, and invalid formats, generating an audit log for traceability.
- **Structural Transformation:** Convert wide-format datasets (ATC drug codes) into a long-format suitable for SQL relational modeling using `pandas.melt`.
- **Data Engineering:** Build a modular pipeline (Extract, Transform, Load) to ingest clean data into a SQLite database.
- **Business Intelligence:** (Upcoming) Execute advanced SQL queries to detect sales patterns and inventory trends.

## 🛠️ Tech Stack
- **Python:** `pandas`, `numpy` (Data manipulation and QA)
- **Database:** `SQLite` (Local relational database)
- **Version Control:** Git & GitHub

## 📂 Project Structure
```
pharma-sales-qa-pipeline/
│
├── data_raw/               # Original raw datasets (not tracked in git)
├── data_clean/             # Processed and validated datasets
├── logs/                   # Directory for logs, rejections CSV, and summary JSON
├── tests/                  # Directory containing unit tests for quality checks
├── extraction_qa.py        # Script for data extraction, unpivot, and QA logging
├── sql_load.py             # Script for database load
├── sql_analytics.sql       # Advanced SQL queries (Market share, MoM growth, date gaps)
├── dashboard.py            # Streamlit interactive QA dashboard
├── main.py                 # Central orchestrator
```

## 📖 Data Dictionary & ATC Glossary

The data warehouse uses the **Anatomical Therapeutic Chemical (ATC) Classification System**, which is the global standard for classifying active substances in drugs.

### ATC Code Glossary
| ATC Code | Drug Group | Real-World Examples |
| :--- | :--- | :--- |
| **M01AB** | Anti-inflammatory / Antirheumatic (Non-Steroids) | Diclofenac, Indometacin |
| **M01AE** | Anti-inflammatory / Antirheumatic (Propionic Acid) | Ibuprofen, Ketoprofen |
| **N02BA** | Other Analgesics and Antipyretics (Salicylic Acid) | Aspirin |
| **N02BE** | Other Analgesics and Antipyretics (Anilides) | Paracetamol (Acetaminophen) |
| **N05B** | Anxiolytics | Diazepam, Alprazolam |
| **N05C** | Hypnotics and Sedatives | Melatonin, Zolpidem |
| **R03** | Drugs for Obstructive Airway Diseases | Salbutamol (Inhalers) |
| **R06** | Antihistamines for Systemic Use | Loratadine, Cetirizine |

### Database Schema (`daily_sales` Table)
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `fecha` | TEXT (ISO Date) | Transaction date (Staged as YYYY-MM-DD) |
| `anio` | INTEGER | Year of transaction |
| `mes` | INTEGER | Month of transaction (1-12) |
| `hora` | INTEGER | Hour of transaction (0-23) |
| `dia_semana` | TEXT | Name of the weekday (e.g., Monday) |
| `codigo_atc` | TEXT | Standardized ATC category code (Foreign key to master) |
| `cantidad_vendida` | REAL | Total quantity sold |

## 📊 Advanced SQL Analytics

The [sql_analytics.sql](file:///c:/Users/javie/Documents/practice-projects/pharma-sales-qa-pipeline/sql_analytics.sql) script contains highly-optimized SQL queries to answer critical business and QA questions:
1. **Market Share & MoM Sales Growth**: Uses Window Functions (`SUM() OVER`, `LAG()`) to compute the monthly market share of each drug category and its Month-over-Month growth rate. This assists in predictive demand forecasting.
2. **QA Data Completeness (Date Gaps)**: Employs `LEAD()` and SQLite's `julianday()` function to automatically audit consecutive sales dates. It identifies any unrecorded days, exposing regional network drops or POS ingestion failures.

## How to Run
1. Ensure Python and dependencies are installed (`pip install pandas numpy pytest streamlit plotly`).
2. Place the `salesdaily.csv` file in the `data_raw/` directory.
3. Run the ETL pipeline: `python main.py`
4. Run unit tests: `pytest tests/test_extraction_qa.py -v`
5. Launch the QA Dashboard: `streamlit run dashboard.py`