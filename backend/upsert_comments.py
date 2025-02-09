import sqlite3
from backend.modules.get_comments import get_youtube_comments

DATABASE = 'youtube_dashboard.db'

def upsert_comments_for_video(video_url, video_id):
    comments_data = get_youtube_comments(video_url)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for comment in comments_data:
        cursor.execute(''' 
            INSERT INTO comments (video_id, comment_text, published_at, like_count, sentiment)
            VALUES (?, ?, ?, ?, NULL)
            ON CONFLICT(comment_id) DO UPDATE SET
                like_count = excluded.like_count
        ''', (video_id, comment['comment'], comment['published_at'], comment['like_count']))
    
    conn.commit()
    conn.close()
