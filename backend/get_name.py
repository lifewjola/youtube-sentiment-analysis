import sqlite3

def get_nickname_by_email(email):
    conn = sqlite3.connect('youtube_dashboard.db')
    cursor = conn.cursor()

    cursor.execute('SELECT nickname FROM user WHERE email = ?', (email,))
    user = cursor.fetchone()

    conn.close()
    return user[0] if user else "" 
