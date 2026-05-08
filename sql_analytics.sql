-- ==============================================================================
-- PHARMA SALES PIPELINE: SQL ANALYTICS & ADVANCED BUSINESS USE CASES
-- ==============================================================================
-- This script contains analytical queries designed to run on the 'daily_sales' table.
-- It demonstrates advanced SQL techniques (Window Functions, CTEs, Date Arithmetic) 
-- to solve key business and QA questions in a pharmaceutical context.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- CASE 1: Monthly ATC Code Trends, Market Share & Month-over-Month (MoM) Growth
-- ------------------------------------------------------------------------------
-- Objective: Understand which ATC categories are growing, their monthly market share,
-- and identify MoM sales trends to support inventory forecasting.
-- ------------------------------------------------------------------------------

WITH monthly_sales AS (
    SELECT 
        anio,
        mes,
        codigo_atc,
        SUM(cantidad_vendida) AS total_sales
    FROM daily_sales
    GROUP BY anio, mes, codigo_atc
),
market_share_and_lag AS (
    SELECT 
        anio,
        mes,
        codigo_atc,
        total_sales,
        -- Total sales for all ATC codes in this specific month
        SUM(total_sales) OVER(PARTITION BY anio, mes) AS total_monthly_market_sales,
        -- Sales from the previous month for MoM growth calculation
        LAG(total_sales, 1) OVER(PARTITION BY codigo_atc ORDER BY anio, mes) AS previous_month_sales
    FROM monthly_sales
)
SELECT 
    anio,
    mes,
    codigo_atc,
    ROUND(total_sales, 2) AS sales_volume,
    -- Market Share %
    ROUND((total_sales * 100.0) / total_monthly_market_sales, 2) AS market_share_percentage,
    ROUND(previous_month_sales, 2) AS prev_month_sales_volume,
    -- Month-over-Month Growth %
    CASE 
        WHEN previous_month_sales IS NULL THEN 0.0
        ELSE ROUND(((total_sales - previous_month_sales) * 100.0) / previous_month_sales, 2)
    END AS mom_growth_percentage
FROM market_share_and_lag
ORDER BY anio, mes, sales_volume DESC;


-- ------------------------------------------------------------------------------
-- CASE 2: QA Audit - Detecting Time Gaps (Missing Sales Days)
-- ------------------------------------------------------------------------------
-- Objective: Detect if there are any missing dates in our sales records.
-- Consecutive sales dates should have a difference of exactly 1 day. Gaps can
-- indicate regional POS outages or ETL ingestion errors.
-- ------------------------------------------------------------------------------

WITH ordered_dates AS (
    SELECT DISTINCT 
        fecha,
        -- Get the next date in sequence
        LEAD(fecha, 1) OVER(ORDER BY fecha) AS next_fecha
    FROM daily_sales
),
date_differences AS (
    SELECT 
        fecha AS current_day,
        next_fecha,
        -- Calculate the difference in days between the current record and the next
        (julianday(next_fecha) - julianday(fecha)) AS days_difference
    FROM ordered_dates
    WHERE next_fecha IS NOT NULL
)
SELECT 
    current_day AS gap_starts_after,
    next_fecha AS gap_ends_on,
    CAST(days_difference - 1 AS INTEGER) AS missing_days_count
FROM date_differences
WHERE days_difference > 1
ORDER BY missing_days_count DESC;
