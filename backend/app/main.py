from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from app.services.youtube import process_comments, extract_video_id
from app.services.scorer import score_all_comments
from app.services.embedder import embed_comments, cluster_topics
from app.services.synthesiser import synthesise
from app.db.supabase import create_job, create_report, save_comments, update_job_status
from collections import Counter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyseRequest(BaseModel):
    video_url: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/report/{slug}")
def get_report(slug: str):
    from app.db.supabase import client
    result = client.table("reports").select("*").eq("slug", slug).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Report not found")
    return result.data[0]

@app.post("/analyse")
async def analyse(request: AnalyseRequest):
    try:
        video_id = extract_video_id(request.video_url)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    job_id = create_job(request.video_url, video_id)

    try:
        update_job_status(job_id, "processing")

        comments = await process_comments(video_id, max_results=100)

        comments = score_all_comments(comments)

        texts = [c["translated"] for c in comments]
        embeddings = embed_comments(texts)
        topics = cluster_topics(texts, embeddings)
        for comment, topic in zip(comments, topics):
            comment["cluster"] = topic

        report_data = synthesise(comments)

        lang_breakdown = dict(Counter(c["language"] for c in comments).most_common(5))
        emotion_breakdown = dict(Counter(c.get("topic", "other") for c in comments).most_common(5))

        report_id, slug = create_report(job_id, lang_breakdown)
        
        from app.db.supabase import client
        client.table("reports").update({
            "emotion_fingerprint": emotion_breakdown,
            "narrative": report_data["narrative"],
            "funniest_comment": report_data["funniest_comment"],
            "unhinged_comment": report_data["most_unhinged_comment"],
            "total_comments": len(comments)
        }).eq("id", report_id).execute()

        save_comments(report_id, comments)
        update_job_status(job_id, "done")

        return {
            "slug": slug,
            "report_id": report_id,
            "job_id": job_id
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        update_job_status(job_id, "failed")
        raise HTTPException(status_code=500, detail=str(e))