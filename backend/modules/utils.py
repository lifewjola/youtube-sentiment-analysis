from urllib.parse import urlparse, parse_qs
import re

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    parsed_url = urlparse(url)
    
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]

    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")
    
    return None 

def break_text_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return sentences

