import sqlite3
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def email_exist(email):

    # compare email with the emails in the database and return true if it exist
    conn = sqlite3.connect('youtube_dashboard.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def verify_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

conn = sqlite3.connect('youtube_dashboard.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nickname TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        youtube_username TEXT NOT NULL UNIQUE
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        video_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        transcript TEXT,
        published_at TEXT,
        video_url TEXT UNIQUE,
        thumbnail_url TEXT,
        views INTEGER,
        likes INTEGER,
        FOREIGN KEY (user_id) REFERENCES user (user_id)
    );
''')



cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id INTEGER,
        comment_text TEXT,
        published_at TEXT,
        like_count INTEGER,
        sentiment TEXT,
        FOREIGN KEY (video_id) REFERENCES videos (video_id)
    );
''')

conn.commit()