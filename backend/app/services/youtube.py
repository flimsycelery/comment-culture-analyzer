from googleapiclient.discovery import build
from app.config import settings
from app.services.sarvam import identify_language, translate_to_english, needs_translation
import asyncio

def extract_video_id(url: str) -> str:
    """Extract video ID from any YouTube URL format"""
    import re
    patterns = [
        r'(?:v=)([a-zA-Z0-9_-]{11})',        # watch?v=ID
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})', # youtu.be/ID
        r'(?:live/)([a-zA-Z0-9_-]{11})',       # /live/ID
        r'(?:shorts/)([a-zA-Z0-9_-]{11})',     # /shorts/ID
        r'(?:embed/)([a-zA-Z0-9_-]{11})',      # /embed/ID
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid YouTube URL")

def fetch_raw_comments(video_id: str, max_results: int = 500) -> list[dict]:
    """Fetch raw comments from YouTube API"""
    youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
    
    comments = []
    page_token = None

    while len(comments) < max_results:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=page_token,
            textFormat="plainText",
            order="relevance"        # returns top/most liked comments first
        ).execute()

        for item in response["items"]:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "text": snippet["textDisplay"],
                "likes": int(snippet["likeCount"]),
                "author": snippet["authorDisplayName"],
                "language": None,
                "translated": None
            })

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    print(f"Fetched {len(comments)} comments")
    return comments
    
async def process_comments(video_id: str, max_results: int = 500) -> list[dict]:
    """Fetch, identify languages, and translate regional comments"""
    comments = fetch_raw_comments(video_id, max_results)

    print("Identifying languages...")
    for comment in comments:
        comment["language"] = await identify_language(comment["text"])

    print("Translating regional comments...")
    translated_count = 0
    for comment in comments:
        if needs_translation(comment["language"]):
            comment["translated"] = await translate_to_english(
                comment["text"],
                comment["language"]
            )
            translated_count += 1
        else:
            comment["translated"] = comment["text"]

    print(f"Translated {translated_count} regional language comments")
    return comments

def fetch_video_metadata(video_id: str) -> dict:
    """Fetch video title and thumbnail"""
    youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
    response = youtube.videos().list(
        part="snippet",
        id=video_id
    ).execute()
    
    if not response["items"]:
        return {"title": "Unknown Video", "thumbnail": "", "channel": ""}
    
    snippet = response["items"][0]["snippet"]
    return {
        "title": snippet["title"],
        "thumbnail": snippet["thumbnails"]["high"]["url"],
        "channel": snippet["channelTitle"]
    }