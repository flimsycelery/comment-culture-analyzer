from supabase import create_client
from app.config import settings
import uuid

client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def create_job(video_url: str, video_id: str) -> str:
    """Create a new analysis job and return job_id"""
    result = client.table("jobs").insert({
        "video_url": video_url,
        "video_id": video_id,
        "status": "processing"
    }).execute()
    return result.data[0]["id"]

def save_comments(report_id: str, comments: list[dict]):
    """Save processed comments to Supabase"""
    rows = [{
        "report_id": report_id,
        "original_text": c["text"],
        "translated_text": c["translated"],
        "detected_language": c["language"],
        "like_count": c["likes"]
    } for c in comments]
    
    for i in range(0, len(rows), 100):
        client.table("comments").insert(rows[i:i+100]).execute()
    
    print(f"Saved {len(rows)} comments to Supabase")

def create_report(job_id: str, language_breakdown: dict) -> str:
    """Create initial report record and return report_id"""
    slug = str(uuid.uuid4())[:8]
    result = client.table("reports").insert({
        "job_id": job_id,
        "slug": slug,
        "language_breakdown": language_breakdown,
    }).execute()
    return result.data[0]["id"], slug

def update_job_status(job_id: str, status: str):
    client.table("jobs").update({"status": status}).eq("id", job_id).execute()