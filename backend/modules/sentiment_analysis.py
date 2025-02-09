import streamlit as st
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import json

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
  "temperature": 1,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}


# Function to analyze sentiment
def analyze_sentiment(video_id, transcript, comments_data):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config
    )
    
    prompt = f"""
    This is the summary of a YouTube video: {transcript}. 
    The following comments were left by viewers of the video: {comments_data}. 
    Analyze the sentiment of the comments and classify them as POSITIVE, NEGATIVE, or NEUTRAL. 
    Return a json object in this format: {[{"comment_id": 1, "sentiment": "POSITIVE"}, {"comment_id": 2, "sentiment": "NEUTRAL"}, {"comment_id": 3, "sentiment": "NEGATIVE"}]}
    Ensure that all the properties i.e. comment_id and sentiment are enclosed in double quotes."""

    
    response = model.generate_content(prompt)
    
    return response.text

