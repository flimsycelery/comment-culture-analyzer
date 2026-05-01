from googleapiclient.discovery import build
from langdetect import detect, LangDetectException
from app.config import settings
from app.services.sarvam import translate_to_english, needs_translation
import asyncio

def extract_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL")

def fetch_comments(video_id: str, max_results: int = 500) -> list[dict]:
    youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
    
    comments = []
    page_token = None

    while len(comments) < max_results:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=page_token,
            textFormat="plainText"
        ).execute()

        for item in response["items"]:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            text = snippet["textDisplay"]
            
            try:
                lang = detect(text)
            except LangDetectException:
                lang = "unknown"

            comments.append({
                "text": text,
                "likes": snippet["likeCount"],
                "author": snippet["authorDisplayName"],
                "language": lang,
                "translated": None
            })

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    print(f"Fetched {len(comments)} comments")
    return comments

async def process_comments(video_id: str, max_results: int = 500) -> list[dict]:
    """Fetch comments and translate regional language ones"""
    comments = fetch_comments(video_id, max_results)
    
    for comment in comments:
        if needs_translation(comment["language"]):
            comment["translated"] = await translate_to_english(
                comment["text"], 
                comment["language"]
            )
        else:
            comment["translated"] = comment["text"]
    
    translated_count = sum(1 for c in comments if c["language"] in ["hi","kn","ta","te","ml","bn","gu","mr"])
    print(f"Translated {translated_count} regional language comments")
    return comments