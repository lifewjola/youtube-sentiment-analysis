import sqlite3

conn = sqlite3.connect("youtube_dashboard.db") 
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in the database:", tables)

conn.close()

conn = sqlite3.connect("youtube_dashboard.db")
cursor = conn.cursor()

table_name = "videos" 
cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000;") 

rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()

import sqlite3

conn = sqlite3.connect("youtube_dashboard.db")
cursor = conn.cursor()

table_name = "comments" 
cursor.execute(f"PRAGMA table_info({table_name});")
schema = cursor.fetchall()

for column in schema:
    print(column)

conn.close()


