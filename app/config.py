import os

class Settings:
    APP_NAME: str = "Personalized Networking Assistant"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pns.db")
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # ML Models Configuration
    THEME_EXTRACTOR_MODEL: str = os.getenv("THEME_EXTRACTOR_MODEL", "typeform/distilbert-base-uncased-mnli")
    STARTER_GENERATOR_MODEL: str = os.getenv("STARTER_GENERATOR_MODEL", "gpt2")
    
    # Toggle to use mock ML services for fast start up
    USE_MOCK_ML: bool = os.getenv("USE_MOCK_ML", "True").lower() in ("true", "1", "yes")

settings = Settings()
