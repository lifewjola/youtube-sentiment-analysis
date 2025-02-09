import sqlite3
from backend.modules.video_metadata import get_video_metadata
from backend.modules.get_transcript import get_youtube_transcript

DATABASE = 'youtube_dashboard.db'

def upsert_video(user_id, video_url):
    """Upsert video metadata, including transcript, into the videos table."""
    try:
        video_metadata = get_video_metadata(video_url)
        if not video_metadata:  
            print(f"Skipping {video_url} due to missing metadata.")
            return  

        transcript = get_youtube_transcript(video_url) or "" 

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM videos WHERE video_url = ?", (video_url,))
            if cursor.fetchone():
                print(f"Video {video_url} already exists.")
                return

            cursor.execute('''
                INSERT OR REPLACE INTO videos (user_id, title, description, transcript, published_at, video_url, thumbnail_url, views, likes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, video_metadata['title'], video_metadata['description'],
                transcript, video_metadata['published_at'], video_metadata['video_url'],
                video_metadata['thumbnail_url'], video_metadata['views'], video_metadata['likes']
            ))

        print(f"Video '{video_metadata['title']}' inserted/updated successfully.")
    
    except Exception as e:
        print(f"Error upserting video {video_url}: {e}")
