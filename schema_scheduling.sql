-- Schema for a multi-location staff scheduling and coverage tracker

CREATE TABLE IF NOT EXISTS employees (
    employee_id     TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    role            TEXT NOT NULL,
    home_location   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shift_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id     TEXT NOT NULL REFERENCES employees(employee_id),
    shift_date      DATE NOT NULL,
    status          TEXT NOT NULL CHECK (status IN ('W', 'V', '!', 'OFF'))
);

CREATE TABLE IF NOT EXISTS admin_coverage (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    location        TEXT NOT NULL,
    coverage_date   DATE NOT NULL,
    status          TEXT NOT NULL CHECK (status IN ('Confirmed', 'Unconfirmed', 'Away'))
);

CREATE INDEX IF NOT EXISTS idx_shift_employee ON shift_log(employee_id);
CREATE INDEX IF NOT EXISTS idx_shift_date ON shift_log(shift_date);
CREATE INDEX IF NOT EXISTS idx_admin_location_date ON admin_coverage(location, coverage_date);
