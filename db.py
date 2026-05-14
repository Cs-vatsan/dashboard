import sqlite3
from datetime import datetime

DB_NAME = "employees.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # EMPLOYEES
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT,
            email TEXT UNIQUE,
            role TEXT,
            active INTEGER DEFAULT 1,
            username TEXT UNIQUE,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # TASKS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            title TEXT,
            status TEXT,
            priority TEXT,
            hours REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    """)

    # WORK LOGS (employee calendar entries)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS work_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            log_date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            hours_worked REAL,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    """)

    # INTERACTIONS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            interaction_type TEXT,
            score INTEGER,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    """)

    # AUDIT LOGS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            performed_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Auto-migrate: add columns if they don't exist yet
    existing = [row[1] for row in cur.execute("PRAGMA table_info(employees)").fetchall()]
    if "username" not in existing:
        cur.execute("ALTER TABLE employees ADD COLUMN username TEXT")
    if "password_hash" not in existing:
        cur.execute("ALTER TABLE employees ADD COLUMN password_hash TEXT")

    conn.commit()
    conn.close()


# ── EMPLOYEE CRUD ──

def add_employee(name, department, email, role, username=None, password_hash=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO employees(name, department, email, role, username, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, department, email, role, username, password_hash))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        raise Exception("Email or username already exists")
    finally:
        conn.close()


def get_employees(active_only=False):
    conn = get_connection()
    cur = conn.cursor()
    if active_only:
        cur.execute("SELECT * FROM employees WHERE active = 1")
    else:
        cur.execute("SELECT * FROM employees")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_employee_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row


def deactivate_employee(employee_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE employees SET active = 0 WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()


def delete_employee(employee_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE employee_id = ?", (employee_id,))
    cur.execute("DELETE FROM work_logs WHERE employee_id = ?", (employee_id,))
    cur.execute("DELETE FROM interactions WHERE employee_id = ?", (employee_id,))
    cur.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()


def update_employee(employee_id, name, department, email, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE employees SET name=?, department=?, email=?, role=? WHERE id=?
    """, (name, department, email, role, employee_id))
    conn.commit()
    conn.close()


# ── TASK CRUD ──

def add_task(employee_id, title, status, priority, hours):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks(employee_id, title, status, priority, hours)
        VALUES (?, ?, ?, ?, ?)
    """, (employee_id, title, status, priority, hours))
    conn.commit()
    conn.close()


def get_tasks(employee_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if employee_id:
        cur.execute("SELECT * FROM tasks WHERE employee_id = ? ORDER BY created_at DESC", (employee_id,))
    else:
        cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_task(task_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def update_task_status(task_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()


# ── WORK LOGS ──

def add_work_log(employee_id, log_date, start_time, end_time, hours_worked, note=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO work_logs(employee_id, log_date, start_time, end_time, hours_worked, note)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (employee_id, log_date, start_time, end_time, hours_worked, note))
    conn.commit()
    conn.close()


def get_work_logs(employee_id=None, month=None, year=None):
    conn = get_connection()
    cur = conn.cursor()
    if employee_id and month and year:
        cur.execute("""
            SELECT * FROM work_logs
            WHERE employee_id = ?
            AND strftime('%m', log_date) = ?
            AND strftime('%Y', log_date) = ?
            ORDER BY log_date ASC
        """, (employee_id, f"{month:02d}", str(year)))
    elif employee_id:
        cur.execute("SELECT * FROM work_logs WHERE employee_id = ? ORDER BY log_date DESC", (employee_id,))
    else:
        cur.execute("SELECT * FROM work_logs ORDER BY log_date DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_work_log(log_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM work_logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()


# ── INTERACTIONS ──

def add_interaction(employee_id, interaction_type, score, note):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO interactions(employee_id, interaction_type, score, note)
        VALUES (?, ?, ?, ?)
    """, (employee_id, interaction_type, score, note))
    conn.commit()
    conn.close()


def get_interactions(employee_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if employee_id:
        cur.execute("SELECT * FROM interactions WHERE employee_id = ? ORDER BY created_at DESC", (employee_id,))
    else:
        cur.execute("SELECT * FROM interactions ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


# ── AUDIT LOGS ──

def log_action(action, performed_by="system"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO audit_logs(action, performed_by) VALUES (?, ?)", (action, performed_by))
    conn.commit()
    conn.close()


def get_audit_logs(limit=100):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


# ── RATING ──

def calculate_employee_rating(employee_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM tasks WHERE employee_id=?", (employee_id,))
    total_tasks = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tasks WHERE employee_id=? AND status='Completed'", (employee_id,))
    completed_tasks = cur.fetchone()[0]

    task_completion_score = (completed_tasks / total_tasks * 100) if total_tasks else 0

    cur.execute("SELECT AVG(score) FROM interactions WHERE employee_id=?", (employee_id,))
    interaction_avg = cur.fetchone()[0] or 0
    interaction_score = (interaction_avg / 5) * 100

    cur.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE employee_id=? AND created_at >= datetime('now', '-30 day')
    """, (employee_id,))
    recent_tasks = cur.fetchone()[0]
    consistency_score = min(100, recent_tasks * 10)

    attendance_score = 90
    final_score = (
        (task_completion_score * 0.4)
        + (interaction_score * 0.3)
        + (consistency_score * 0.2)
        + (attendance_score * 0.1)
    )
    conn.close()
    return round(final_score / 20, 1)