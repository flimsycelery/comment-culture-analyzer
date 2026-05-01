from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    YOUTUBE_API_KEY:str
    SARVAM_API_KEY:str
    GROQ_API_KEY:str
    SUPABASE_URL:str
    SUPABASE_SERVICE_KEY:str

    class Config:
        env_file=".env"
    
settings=Settings()