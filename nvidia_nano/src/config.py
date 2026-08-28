import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    NEBIUS_API_KEY: str = os.getenv("NEBIUS_API_KEY", "mock-nebius-key")
    NEBIUS_BASE_URL: str = os.getenv("NEBIUS_BASE_URL", "https://api.studio.nebius.ai/v1/")
    
    # NVIDIA open-source models served on Nebius Token Factory
    MODEL_ULTRA: str = os.getenv("MODEL_NVIDIA_NEMOTRON_ULTRA", "nvidia/nemotron-4-340b-instruct")
    MODEL_NANO: str = os.getenv("MODEL_NVIDIA_NEMOTRON_NANO", "nvidia/nemotron-4-8b-instruct")
    
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

settings = Settings()
