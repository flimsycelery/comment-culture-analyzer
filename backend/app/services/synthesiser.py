from groq import Groq
from app.config import settings
from collections import Counter
import json

client = Groq(api_key=settings.GROQ_API_KEY)

SYNTHESIS_PROMPT = """You are analysing a YouTube video's comment section.
Based on the data below, write a cultural analysis report.

Video stats:
- Total comments analysed: {total}
- Language breakdown: {languages}
- Emotion breakdown: {emotions}
- Average toxicity: {avg_toxicity}/10
- Average humour: {avg_humour}/10
- Top topics: {topics}

Sample comments (translated to English):
{sample_comments}

Return ONLY a valid JSON object in this exact format, no markdown, no backticks:
{{
  "narrative": "3-4 sentence cultural analysis of this comment section. Be specific, insightful and mention the languages and cultural context.",
  "funniest_comment": "the single funniest comment from the samples",
  "most_unhinged_comment": "the most chaotic or unhinged comment from the samples",
  "vibe": "one word that captures the overall vibe e.g. nostalgic, chaotic, wholesome, toxic, hype"
}}"""

def synthesise(comments: list[dict]) -> dict:
    """Generate final report narrative using Groq"""
    
    total = len(comments)
    languages = dict(Counter(c["language"] for c in comments).most_common(5))
    emotions = dict(Counter(c.get("topic", "other") for c in comments).most_common(5))
    
    scored = [c for c in comments if "toxicity" in c]
    avg_toxicity = round(sum(c["toxicity"] for c in scored) / len(scored), 1) if scored else 0
    avg_humour = round(sum(c["humour"] for c in scored) / len(scored), 1) if scored else 0
    
    sample = sorted(comments, key=lambda x: x.get("likes", 0), reverse=True)[:20]
    sample_text = "\n".join(f"- {c['translated'][:100]}" for c in sample)
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role": "user",
            "content": SYNTHESIS_PROMPT.format(
                total=total,
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