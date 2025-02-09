import sqlite3
from backend.database import verify_password

def authenticate_user(email, password):
    conn = sqlite3.connect('youtube_dashboard.db')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT password_hash FROM user WHERE email = ?
    ''', (email,))
    result = cursor.fetchone()

    if result is None:
        conn.close()
        raise ValueError(f"Authentication failed: No user found with email {email}")

    stored_hash = result[0]
    conn.close()

    if not verify_password(stored_hash, password):
        raise ValueError("Authentication failed: Incorrect password")

    return True 