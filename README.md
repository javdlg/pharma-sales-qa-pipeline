# Pharma Sales Data QA & Analytics Pipeline

## 📌 Project Overview
This project demonstrates an end-to-end Data Analytics and Quality Assurance (QA) pipeline for pharmaceutical sales data. It focuses on extracting raw transactional data, applying strict business rules for data cleansing, transforming structures for relational databases, and ensuring high data reliability.

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
├── 1_extraction_and_qa.py  # Script for data extraction, unpivot, and QA logging
└── README.md
```

## How to Run
- 1. Ensure Python is installed.
- 2. Place the `salesdaily.csv` file in the `data_raw/` directory.
- 3. Run the script `python 01_extraction_qa.py`.