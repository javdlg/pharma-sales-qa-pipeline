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
├── extraction_qa.py        # Script for data extraction, unpivot, and QA logging
├── sql_load.py             # Script for database load
```

## How to Run
- Ensure Python is installed.
- Place the `salesdaily.csv` file in the `data_raw/` directory.
- Run the pipeline with `python main.py`.