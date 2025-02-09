import sqlite3
from backend.database import hash_password

def create_user(nick_name, email, password, youtube_username):
    conn = sqlite3.connect('youtube_dashboard.db')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM user WHERE email = ?
    ''', (email,))
    result = cursor.fetchone()
    if result:
        conn.close()
        raise ValueError(f"User with email {email} already exists")

    password_hash = hash_password(password)

    cursor.execute('''
    INSERT INTO user (nickname, email, password_hash, youtube_username)
    VALUES (?, ?, ?, ?)
    ''', (nick_name, email, password_hash, youtube_username))

    conn.commit()
    user_id = cursor.lastrowid 
    conn.close()

    return True  

       
