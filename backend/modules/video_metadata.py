import googleapiclient.discovery
import googleapiclient.errors
import streamlit as st
from backend.modules.utils import extract_video_id

YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_video_metadata(video_url):
    """Retrieve metadata for a given YouTube video URL."""
    vid_id = extract_video_id(video_url)
    
    try:
        request = youtube.videos().list(
            part="snippet,statistics",
            id=vid_id
        )
        response = request.execute()
        
        if response["items"]:
            video_data = response["items"][0]
            title = video_data["snippet"]["title"]
            description = video_data["snippet"].get("description", "")
            published_at = video_data["snippet"]["publishedAt"]
            video_url = f"https://www.youtube.com/watch?v={vid_id}"
            thumbnail_url = video_data["snippet"].get("thumbnails", {}).get("default", {}).get("url", "")
            views = int(video_data["statistics"].get("viewCount", 0))
            likes = int(video_data["statistics"].get("likeCount", 0))

            return {
                "title": title,
                "description": description,
                "published_at": published_at,
                "video_url": video_url,
                "thumbnail_url": thumbnail_url,
                "views": views,
                "likes": likes
            }
        else:
            raise ValueError(f"Video with ID {vid_id} not found.")
    except googleapiclient.errors.HttpError as e:
        raise ValueError(f"Error retrieving video metadata: {e}")
