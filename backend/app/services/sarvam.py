import httpx
from app.config import settings

SUPPORTED_LANGS = {"hi", "kn", "ta", "te", "ml", "bn", "gu", "mr"}

async def identify_language(text: str) -> str:
    """Use Sarvam to identify Indian languages including Hinglish"""
    if len(text.strip()) < 5:
        return "unknown"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.sarvam.ai/text-lid",
            headers={
                "api-subscription-key": settings.SARVAM_API_KEY,
                "Content-Type": "application/json"
            },
            json={"input": text}
        )
        result = response.json()
        lang = result.get("language_code", "unknown")
        return lang

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
                "source_language_code": source_lang,
                "target_language_code": "en-IN",
                "speaker_gender": "Male",
                "mode": "formal",
                "enable_preprocessing": True
            }
        )
        result = response.json()
        return result.get("translated_text", text)

def needs_translation(lang: str) -> bool:
    """Check if comment needs translation - includes Hinglish (hi-Latn)"""
    if not lang:
        return False
    base_lang = lang.split("-")[0]
    return base_lang in SUPPORTED_LANGS and lang != "en-Latn"