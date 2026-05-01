import httpx
from app.config import settings

SUPPORTED_LANGS = {"hi", "kn", "ta", "te", "ml", "bn", "gu", "mr"}

async def translate_to_english(text: str, source_lang: str) -> str:
    """Translate Indian language text to English using Sarvam AI"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.sarvam.ai/translate",
            headers={
                "api-subscription-key": settings.SARVAM_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "input": text,
                "source_language_code": f"{source_lang}-IN",
                "target_language_code": "en-IN",
                "speaker_gender": "Male",
                "mode": "formal",
                "enable_preprocessing": True
            }
        )
        result = response.json()
        return result.get("translated_text", text)

def needs_translation(lang: str) -> bool:
    """Check if a comment needs translation"""
    return lang in SUPPORTED_LANGS