from googleapiclient.discovery import build
from langdetect import detect, LangDetectException
from app.config import settings

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
                "language": lang
            })

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    print(f"Fetched {len(comments)} comments")
    return comments