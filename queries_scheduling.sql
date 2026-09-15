-- Analytical queries for the staff scheduling tracker
-- Demonstrates: JOINs, aggregation, CASE, window functions, subqueries

-- 1. Daily nail/brow master coverage count, flagged by minimum thresholds
SELECT
    s.shift_date,
    SUM(CASE WHEN e.role = 'Nail Master' AND s.status = 'W' THEN 1 ELSE 0 END) AS nail_masters_working,
    SUM(CASE WHEN e.role = 'Brow Master' AND s.status = 'W' THEN 1 ELSE 0 END) AS brow_masters_working,
    CASE
        WHEN SUM(CASE WHEN e.role = 'Nail Master' AND s.status = 'W' THEN 1 ELSE 0 END) >= 9 THEN 'Strong'
        WHEN SUM(CASE WHEN e.role = 'Nail Master' AND s.status = 'W' THEN 1 ELSE 0 END) >= 7 THEN 'Acceptable'
        ELSE 'Below minimum'
    END AS coverage_flag
FROM shift_log s
JOIN employees e ON e.employee_id = s.employee_id
GROUP BY s.shift_date
ORDER BY s.shift_date;

-- 2. Employees with the most unplanned absences ('!') in the month
SELECT e.name, e.role, COUNT(*) AS unplanned_absences
FROM shift_log s
JOIN employees e ON e.employee_id = s.employee_id
WHERE s.status = '!'
GROUP BY e.employee_id, e.name, e.role
ORDER BY unplanned_absences DESC;

-- 3. Weekly average nail master coverage (window function over week number)
SELECT
    week_number,
    ROUND(AVG(nail_masters_working), 1) AS avg_nail_masters
FROM (
    SELECT
        s.shift_date,
        CAST(strftime('%j', s.shift_date) AS INTEGER) / 7 + 1 AS week_number,
        SUM(CASE WHEN e.role = 'Nail Master' AND s.status = 'W' THEN 1 ELSE 0 END) AS nail_masters_working
    FROM shift_log s
    JOIN employees e ON e.employee_id = s.employee_id
    GROUP BY s.shift_date
) daily
GROUP BY week_number
ORDER BY week_number;

-- 4. Locations with unresolved admin coverage gaps (Away or Unconfirmed)
SELECT location, coverage_date, status
FROM admin_coverage
WHERE status IN ('Away', 'Unconfirmed')
ORDER BY coverage_date, location;

-- 5. Admin coverage reliability by location (% confirmed)
SELECT
    location,
    ROUND(100.0 * SUM(CASE WHEN status = 'Confirmed' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_confirmed
FROM admin_coverage
GROUP BY location
ORDER BY pct_confirmed ASC;
