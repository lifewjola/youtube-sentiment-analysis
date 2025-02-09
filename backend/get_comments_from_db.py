import sqlite3

DATABASE = 'youtube_dashboard.db'

def get_comments(video_id):
    """Retrieve comment_id and comment_text for a given video_id."""
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT comment_id, comment_text 
                FROM comments 
                WHERE video_id = ?
            ''', (video_id,))
            
            comments = cursor.fetchall() 
            
        return [[str(comment_id), comment_text] for comment_id, comment_text in comments]  # Convert to list of lists
    
    except Exception as e:
        print(f"Error retrieving comments: {e}")
        return []
