from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable
import re
import requests
import os
from dotenv import load_dotenv
from functools import lru_cache
import time
import logging

load_dotenv()  # Load environment variables from .env

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_video_id(youtube_url):
    try:
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
        logger.warning(f"Invalid YouTube URL format: {youtube_url}")
        return None
    except Exception as e:
        logger.error(f"Error extracting video ID: {str(e)}")
        return None

def get_transcript(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return None, "❌ Invalid YouTube URL"

    try:
        # First, try to list available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get English transcript first, then fallback to others
        languages_to_try = ['en', 'en-US']
        for lang in languages_to_try:
            try:
                transcript = transcript_list.find_transcript([lang])
                transcript_data = transcript.fetch()
                return transcript_data, None
            except NoTranscriptFound:
                continue
        
        # If no English transcript found, try any available language
        try:
            transcript = transcript_list.find_transcript()
            transcript_data = transcript.fetch()
            return transcript_data, None
        except NoTranscriptFound:
            available_langs = [t.language_code for t in transcript_list]
            return None, f"""
            ❌ No transcript available for this video. 
            
            Available languages: {available_langs}
            
            Please try:
            1. A different video
            2. A video with English subtitles
            3. One of these example videos:
               - https://www.youtube.com/watch?v=dQw4w9WgXcQ
               - https://www.youtube.com/watch?v=9bZkp7q19f0
            """
    except VideoUnavailable:
        return None, "❌ This video is unavailable or private."
    except Exception as e:
        return None, f"❌ Error fetching transcript: {str(e)}"

@lru_cache(maxsize=100)
def get_video_details(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return None, "❌ Invalid YouTube URL"

    try:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            return None, "❌ YouTube API key not found in environment variables."
        
        url = f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={api_key}"
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            return None, f"❌ YouTube API Error: {data['error']['message']}"

        if not data.get("items"):
            return None, "❌ Video details not found."

        item = data["items"][0]
        details = {
            "title": item["snippet"]["title"],
            "views": item["statistics"].get("viewCount", 0),
            "likes": item["statistics"].get("likeCount", 0),
            "comments": item["statistics"].get("commentCount", 0),
            "timestamp": time.time()  # Add timestamp for cache invalidation
        }
        return details, None
    except requests.exceptions.RequestException as e:
        return None, f"❌ Network error fetching video details: {str(e)}"
    except Exception as e:
        return None, f"❌ Error fetching video details: {str(e)}"