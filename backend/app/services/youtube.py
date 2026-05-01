from googleapiclient.discovery import build
from app.config import settings
from app.services.sarvam import identify_language, translate_to_english, needs_translation
import asyncio

def extract_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "/live/" in url:
        return url.split("/live/")[1].split("?")[0]
    else:
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
            textFormat="plainText"
        ).execute()

        for item in response["items"]:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "text": snippet["textDisplay"],
                "likes": snippet["likeCount"],
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