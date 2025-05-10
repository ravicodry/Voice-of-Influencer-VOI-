from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable
import re
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

def extract_video_id(youtube_url):
    # Supports many YouTube URL formats
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    return None

def get_transcript(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return None, "❌ Invalid YouTube URL"

    try:
        # First try to get English transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return transcript_list, None
    except NoTranscriptFound:
        try:
            # If English not available, try any available language
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript_list, None
        except NoTranscriptFound:
            return None, "❌ No transcript available for this video. Please try a different video with subtitles enabled."
        except VideoUnavailable:
            return None, "❌ This video is unavailable or private."
        except Exception as e:
            return None, f"❌ Error fetching transcript: {str(e)}"
    except VideoUnavailable:
        return None, "❌ This video is unavailable or private."
    except Exception as e:
        return None, f"❌ Error fetching transcript: {str(e)}"

def get_video_details(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return None, "❌ Invalid YouTube URL"

    try:
        api_key = os.getenv("YOUTUBE_API_KEY")  # Get API key from environment variable
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
        }
        return details, None
    except requests.exceptions.RequestException as e:
        return None, f"❌ Network error fetching video details: {str(e)}"
    except Exception as e:
        return None, f"❌ Error fetching video details: {str(e)}"