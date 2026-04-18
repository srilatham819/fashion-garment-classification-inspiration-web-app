from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Atelier Lens AI"
    database_url: str = "postgresql+psycopg://fashion:fashion@localhost:5432/fashion_ai"
    openai_api_key: str | None = None
    openai_vision_model: str = "gpt-5.4-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    faiss_index_path: str = "infra/faiss/fashion.index"
    upload_storage_path: str = "backend/storage/uploads"
    max_upload_bytes: int = 10 * 1024 * 1024
    auto_create_tables: bool = True
    demo_ai_fallback: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
