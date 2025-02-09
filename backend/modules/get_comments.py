import googleapiclient.discovery
import streamlit as st
import re
from backend.modules.utils import extract_video_id

YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_youtube_comments(video_url, max_comments=500): 
    video_id = extract_video_id(video_url)
        
    if not video_id:
        raise ValueError("Invalid YouTube URL")

    comments_data = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText",
        maxResults=100 
    )
    
    response = request.execute()

    while request is not None and len(comments_data) < max_comments:
        for item in response['items']:
            if len(comments_data) >= max_comments:
                break 
            
            comment_data = {
                'comment': item['snippet']['topLevelComment']['snippet']['textDisplay'],
                'like_count': item['snippet']['topLevelComment']['snippet']['likeCount'],
                'published_at': item['snippet']['topLevelComment']['snippet']['publishedAt'],
            }
            comments_data.append(comment_data)
        
        if len(comments_data) >= max_comments:
            break

        if 'nextPageToken' in response:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=response['nextPageToken'],
                textFormat="plainText",
                maxResults=100
            )
            response = request.execute()
        else:
            request = None
    
    return comments_data
