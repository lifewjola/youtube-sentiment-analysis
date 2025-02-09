import sqlite3


def upsert_user(user_id, nick_name=None, email=None, youtube_username=None):
    conn = sqlite3.connect('youtube_dashboard.db')
    cursor = conn.cursor()

    if nick_name:
        cursor.execute('''
        UPDATE user SET nick_name = ? WHERE user_id = ?
        ''', (nick_name, user_id))

    if email:
        cursor.execute('''
        UPDATE user SET email = ? WHERE user_id = ?
        ''', (email, user_id))

    if youtube_username:
        cursor.execute('''
        UPDATE user SET youtube_username = ? WHERE user_id = ?
        ''', (youtube_username, user_id))

    conn.commit()
    conn.close()
