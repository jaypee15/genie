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
    
    google_api_key: str
    tavily_api_key: str
    
    temporal_address: str
    temporal_namespace: str
    temporal_api_key: str
    temporal_use_tls: bool = True
    
    app_name: str = "Genie"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str
    
    allowed_origins: str = "http://localhost:5174,http://localhost:3000"
    
    scraping_rate_limit: int = 2
    scraping_user_agent: str = "Genie-Bot/1.0"
    
    # Search optimization settings
    min_internal_opportunities: int = 20  # Minimum relevant opportunities before skipping web scrape
    internal_search_relevance_threshold: float = 0.7  # Minimum similarity score for internal search
    
    # Tavily settings
    enable_tavily_for_jobs: bool = True
    enable_tavily_for_speaking: bool = True
    enable_tavily_for_events: bool = True
    enable_tavily_for_grants: bool = True
    tavily_max_results: int = 15
    tavily_search_depth: str = "advanced"  # "basic" or "advanced"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()

