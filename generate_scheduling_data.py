"""
Generates a synthetic dataset modelling a monthly staff rota for a
multi-role salon team, plus cross-location admin coverage.
All names, locations and figures are fictional.
"""
import csv
import random
from datetime import date, timedelta

random.seed(7)

ROLES = ["Nail Master", "Nail Master", "Nail Master", "Nail Master",
         "Nail Master", "Nail Master", "Nail Master", "Nail Master",
         "Brow Master", "Brow Master", "Administrator", "Administrator", "Cleaner"]

FIRST_NAMES = ["Olena", "Maria", "Sofia", "Nadia", "Iryna", "Kateryna", "Anna",
               "Vika", "Diana", "Yana", "Alina", "Marta", "Lesia"]

LOCATIONS = ["North Studio", "Riverside", "Market Square", "Garden Court",
             "Park Lane", "Old Town"]

START = date(2026, 6, 1)
DAYS = 30
CODES = ["W", "W", "W", "W", "W", "V", "!", ""]  # weighted toward Working


def make_employees():
    employees = []
    for i, role in enumerate(ROLES):
        employees.append({
            "employee_id": f"E{i+1:03d}",
            "name": f"{FIRST_NAMES[i % len(FIRST_NAMES)]} {chr(65 + i)}.",
            "role": role,
            "home_location": "North Studio",
        })
    return employees


def generate_shift_log(employees):
    rows = []
    for emp in employees:
        for d in range(DAYS):
            shift_date = START + timedelta(days=d)
            # Nail/brow masters work more; admin/cleaner fixed patterns
            if emp["role"] in ("Nail Master", "Brow Master"):
                code = random.choices(CODES, weights=[5, 5, 5, 5, 5, 1, 1, 2])[0]
            else:
                code = random.choices(["W", "", "V"], weights=[6, 3, 1])[0]
            rows.append({
                "employee_id": emp["employee_id"],
                "name": emp["name"],
                "role": emp["role"],
                "shift_date": shift_date.isoformat(),
                "status": code if code else "OFF",
            })
    return rows


def generate_admin_coverage():
    rows = []
    for d in range(DAYS):
        shift_date = START + timedelta(days=d)
        for loc in LOCATIONS:
            status = random.choices(
                ["Confirmed", "Unconfirmed", "Away"], weights=[7, 2, 1]
            )[0]
            rows.append({
                "location": loc,
                "coverage_date": shift_date.isoformat(),
                "status": status,
            })
    return rows


def main():
    employees = make_employees()
    shift_rows = generate_shift_log(employees)
    admin_rows = generate_admin_coverage()

    with open("/home/claude/staff-scheduling-analytics/data/shift_log.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(shift_rows[0].keys()))
        writer.writeheader()
        writer.writerows(shift_rows)

    with open("/home/claude/staff-scheduling-analytics/data/admin_coverage.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(admin_rows[0].keys()))
        writer.writeheader()
        writer.writerows(admin_rows)

    print(f"Generated {len(shift_rows)} shift log rows and {len(admin_rows)} admin coverage rows.")


if __name__ == "__main__":
    main()
