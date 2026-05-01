from groq import Groq
import json
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

SCORE_PROMPT = """You are analysing YouTube comments. Score each comment below.
Return ONLY a valid JSON array, no explanation, no markdown, no backticks.
One object per comment in this exact format:
[
  {{
    "sentiment": "positive" or "negative" or "neutral",
    "toxicity": 0-10,
    "humour": 0-10,
    "topic": "hype" or "nostalgia" or "political" or "grief" or "cringe" or "appreciation" or "roast" or "other"
  }}
]

Comments to score:
{comments}"""

def score_batch(comments: list[str]) -> list[dict]:
    """Score a batch of comments using Groq"""
    numbered = "\n".join(f"{i+1}. {c}" for i, c in enumerate(comments))

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": SCORE_PROMPT.format(comments=numbered)
        }],
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()

    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            if part.startswith("json"):
                raw = part[4:].strip()
                break
            elif part.strip().startswith("["):
                raw = part.strip()
                break

    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"Warning: JSON parsing failed, using fallback scores")
        return [{"sentiment": "neutral", "toxicity": 0, "humour": 0, "topic": "other"}] * len(comments)

def score_all_comments(comments: list[dict]) -> list[dict]:
    """Score all comments in batches of 20"""
    translated_texts = [c["translated"] for c in comments]
    all_scores = []

    batch_size = 20
    for i in range(0, len(translated_texts), batch_size):
        batch = translated_texts[i:i+batch_size]
        print(f"Scoring batch {i//batch_size + 1}/{(len(translated_texts)-1)//batch_size + 1}...")
        scores = score_batch(batch)
        all_scores.extend(scores)

    for comment, score in zip(comments, all_scores):
        comment.update(score)

    return comments