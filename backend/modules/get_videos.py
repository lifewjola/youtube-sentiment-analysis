import googleapiclient.discovery
import streamlit as st

YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_channel_id_from_username(username):
    """Retrieve the channel ID from the YouTube username (handle)."""
    username = username.lstrip('@')
    
    request = youtube.search().list(
        part="snippet",
        q=username,
        type="channel",
        maxResults=1 
    )
    response = request.execute()

    if "items" in response and len(response["items"]) > 0:
        return response["items"][0]["snippet"]["channelId"]
    else:
        raise ValueError(f"Channel with username {username} not found.")

def get_video_urls_from_channel(channel_id):
    """Retrieve all video URLs from a YouTube channel using its channel ID."""
    video_urls = []
    
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50, 
        order="date"  
    )
    
    response = request.execute()

    for item in response["items"]:
        if item["id"]["kind"] == "youtube#video":
            video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            video_urls.append(video_url)
    
    while "nextPageToken" in response:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,
            pageToken=response["nextPageToken"],
            order="date"
        )
        response = request.execute()

        for item in response["items"]:
            if item["id"]["kind"] == "youtube#video":
                video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                video_urls.append(video_url)

    return video_urls

def get_video_urls_from_username(username):
    """Main function to get all video URLs from a YouTube username."""
    try:
        channel_id = get_channel_id_from_username(username)
        video_urls = get_video_urls_from_channel(channel_id)
        return video_urls
    except ValueError as e:
        return str(e)
