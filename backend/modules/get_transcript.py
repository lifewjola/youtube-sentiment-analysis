from youtube_transcript_api import YouTubeTranscriptApi
from backend.modules.utils import extract_video_id, break_text_into_sentences

def get_youtube_transcript(url):
    video_id = extract_video_id(url)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry["text"] for entry in transcript])
        sentences = break_text_into_sentences(text)
        return "\n".join(sentences)
    except Exception as e:
        return str(e)
