from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_secret: str
    database_url: str
    
    openai_api_key: str
    
    temporal_address: str
    temporal_namespace: str
    temporal_api_key: str
    
    ably_api_key: str
    
    app_name: str = "Genie"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str
    
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    
    scraping_rate_limit: int = 2
    scraping_user_agent: str = "Genie-Bot/1.0"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()

