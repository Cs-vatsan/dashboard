import bcrypt
from db import get_employee_by_username

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = bcrypt.hashpw(b"admin123", bcrypt.gensalt())


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def authenticate(username: str, password: str):
    """
    Returns:
        ("admin", None)              — admin login
        ("employee", employee_row)   — employee login
        None                         — failed
    """
    # Admin check
    if username == ADMIN_USERNAME:
        if bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH):
            return ("admin", None)
        return None

    # Employee check
    row = get_employee_by_username(username)
    if row is None:
        return None

    # row columns: id, name, department, email, role, active, username, password_hash, created_at
    stored_hash = row[7]
    if stored_hash and bcrypt.checkpw(password.encode(), stored_hash.encode()):
        if row[5] == 0:   # active flag
            return None   # deactivated
        return ("employee", row)
    return None