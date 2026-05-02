from groq import Groq
from app.config import settings
from collections import Counter
import json

client = Groq(api_key=settings.GROQ_API_KEY)

SYNTHESIS_PROMPT = """You are a cultural analyst specialising in internet communities and online discourse.

You have analysed {total} comments from a YouTube video titled "{title}" by "{channel}".

Data:
- Language breakdown: {languages}
- Emotion breakdown: {emotions}
- Average toxicity score: {avg_toxicity}/10
- Average humour score: {avg_humour}/10
- Top topics: {topics}

Top 20 most liked comments:
{sample_comments}

Write a sharp, specific cultural analysis. Rules:
- Be SPECIFIC to THIS video and THIS comment section — not generic
- Only mention languages if they reveal something interesting about the audience
- Do NOT assume or push any regional/national identity unless the data clearly shows it
- Identify recurring themes, references, or inside jokes if present
- Comment on the emotional tone and WHY given the video content
- Write like a culture journalist — analytical, sharp, no fluff

Return ONLY valid JSON, no markdown, no backticks:
{{
  "narrative": "4-5 sentence sharp cultural analysis specific to this video.",
  "funniest_comment": "the single funniest or most witty comment from the samples",
  "most_unhinged_comment": "the most chaotic or dramatic comment",
  "vibe": "one word capturing the overall vibe",
  "audience_type": "one sentence describing who is watching based purely on the data"
}}"""

def synthesise(comments: list[dict], title: str = "", channel: str = "") -> dict:
    """Generate final report narrative using Groq"""
    
    total = len(comments)
    languages = dict(Counter(c["language"] for c in comments).most_common(5))
    emotions = dict(Counter(c.get("topic", "other") for c in comments).most_common(5))
    
    scored = [c for c in comments if "toxicity" in c]
    avg_toxicity = round(sum(c["toxicity"] for c in scored) / len(scored), 1) if scored else 0
    avg_humour = round(sum(c["humour"] for c in scored) / len(scored), 1) if scored else 0
    
    sample = sorted(comments, key=lambda x: x.get("likes", 0), reverse=True)[:20]
    sample_text = "\n".join(f"- [{c.get('likes',0)} likes] {c['translated'][:120]}" for c in sample)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": SYNTHESIS_PROMPT.format(
                total=total,
                title=title,
                channel=channel,
                languages=languages,
                emotions=emotions,
                avg_toxicity=avg_toxicity,
                avg_humour=avg_humour,
                topics=list(emotions.keys()),
                sample_comments=sample_text
            )
        }],
        temperature=0.7
    )
    
    raw = response.choices[0].message.content.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    return json.loads(raw)