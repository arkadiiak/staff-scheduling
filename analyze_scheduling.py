"""
Staff Scheduling Analysis
--------------------------
Loads the synthetic shift log and admin coverage datasets into SQLite,
then uses pandas to analyze daily coverage, flag understaffed days,
and visualize weekly staffing trends.
"""

import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SHIFT_CSV = BASE_DIR / "data" / "shift_log.csv"
ADMIN_CSV = BASE_DIR / "data" / "admin_coverage.csv"
SCHEMA_PATH = BASE_DIR / "sql" / "schema_scheduling.sql"
DB_PATH = BASE_DIR / "python" / "staff_scheduling.db"


def build_database():
    shift_df = pd.read_csv(SHIFT_CSV)
    admin_df = pd.read_csv(ADMIN_CSV)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())

    employees = shift_df[["employee_id", "name", "role"]].drop_duplicates()
    employees["home_location"] = "North Studio"
    employees.to_sql("employees", conn, if_exists="replace", index=False)

    shift_df[["employee_id", "shift_date", "status"]].to_sql(
        "shift_log", conn, if_exists="append", index=False
    )
    admin_df.to_sql("admin_coverage", conn, if_exists="append", index=False)

    conn.commit()
    return conn


def daily_coverage(conn):
    query = """
        SELECT
            s.shift_date,
            SUM(CASE WHEN e.role = 'Nail Master' AND s.status = 'W' THEN 1 ELSE 0 END) AS nail_masters_working,
            SUM(CASE WHEN e.role = 'Brow Master' AND s.status = 'W' THEN 1 ELSE 0 END) AS brow_masters_working
        FROM shift_log s
        JOIN employees e ON e.employee_id = s.employee_id
        GROUP BY s.shift_date
        ORDER BY s.shift_date
    """
    df = pd.read_sql(query, conn)

    def flag(row):
        if row["nail_masters_working"] >= 9:
            return "Strong"
        elif row["nail_masters_working"] >= 7:
            return "Acceptable"
        return "Below minimum"

    df["coverage_flag"] = df.apply(flag, axis=1)
    return df


def unplanned_absences(conn):
    query = """
        SELECT e.name, e.role, COUNT(*) AS unplanned_absences
        FROM shift_log s
        JOIN employees e ON e.employee_id = s.employee_id
        WHERE s.status = '!'
        GROUP BY e.employee_id, e.name, e.role
        ORDER BY unplanned_absences DESC
    """
    return pd.read_sql(query, conn)


def admin_reliability(conn):
    query = """
        SELECT location,
               ROUND(100.0 * SUM(CASE WHEN status = 'Confirmed' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_confirmed
        FROM admin_coverage
        GROUP BY location
        ORDER BY pct_confirmed ASC
    """
    return pd.read_sql(query, conn)


def plot_daily_coverage(coverage_df):
    import matplotlib.pyplot as plt

    coverage_df["shift_date"] = pd.to_datetime(coverage_df["shift_date"])
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(coverage_df["shift_date"], coverage_df["nail_masters_working"], marker="o", label="Nail Masters")
    ax.plot(coverage_df["shift_date"], coverage_df["brow_masters_working"], marker="o", label="Brow Masters")
    ax.axhline(7, color="orange", linestyle="--", label="Nail Master minimum (7)")
    ax.set_title("Daily Staff Coverage — June 2026")
    ax.set_ylabel("Staff working")
    ax.legend()
    plt.tight_layout()
    plt.savefig(BASE_DIR / "python" / "daily_coverage.png")
    print("Chart saved to python/daily_coverage.png")


def main():
    conn = build_database()

    coverage_df = daily_coverage(conn)
    print("\n=== Daily coverage (first 10 days) ===")
    print(coverage_df.head(10).to_string(index=False))

    print("\n=== Days below minimum nail master coverage ===")
    print(coverage_df[coverage_df["coverage_flag"] == "Below minimum"].to_string(index=False))

    print("\n=== Employees with most unplanned absences ===")
    print(unplanned_absences(conn).to_string(index=False))

    print("\n=== Admin coverage reliability by location ===")
    print(admin_reliability(conn).to_string(index=False))

    plot_daily_coverage(coverage_df)
    conn.close()


if __name__ == "__main__":
    main()
