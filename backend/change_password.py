import sqlite3
from database import hash_password

def change_password(user_id, new_password):
    conn = sqlite3.connect('youtube_dashboard.db')
    cursor = conn.cursor()

    new_password_hash = hash_password(new_password)

    cursor.execute('''
    UPDATE user SET password_hash = ? WHERE user_id = ?
    ''', (new_password_hash, user_id))

    conn.commit()
    conn.close()
