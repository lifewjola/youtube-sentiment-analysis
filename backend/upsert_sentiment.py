import sqlite3
from backend.modules.sentiment_analysis import analyze_sentiment
import json

def analyze_sentiment_for_video(video_id):
    """Analyze sentiment of comments for a specific video and upsert into the comments table."""
    
    try:
        conn = sqlite3.connect('youtube_dashboard.db')
        cursor = conn.cursor()
        
        cursor.execute(''' 
            SELECT transcript FROM videos WHERE video_id = ?
        ''', (video_id,))
        video_row = cursor.fetchone()
        
        if video_row is None:
            raise ValueError(f"No video found with ID {video_id}")
        
        transcript = video_row[0]
        
        cursor.execute('''
            SELECT comment_id, comment_text FROM comments WHERE video_id = ?
        ''', (video_id,))
        comments = cursor.fetchall()
        
        comments_data = [{"comment_id": comment[0], "comment_text": comment[1]} for comment in comments]
        
        sentiment_json = analyze_sentiment(video_id, transcript, comments_data)
        cleaned_response = sentiment_json.strip('```json\n').strip()
        sentiment_json = json.loads(cleaned_response)
        
        for sentiment in sentiment_json:
            comment_id = sentiment['comment_id']
            sentiment_value = sentiment['sentiment']
            
            cursor.execute('''
                UPDATE comments
                SET sentiment = ?
                WHERE comment_id = ?
            ''', (sentiment_value, comment_id))
        
        conn.commit()
        conn.close()
        print(f"Sentiment analysis for video {video_id} completed and comments updated.")
    
    except Exception as e:
        print(sentiment_json)
        print(cleaned_response)
        print(f"Error analyzing sentiment for video {video_id}: {e}")
