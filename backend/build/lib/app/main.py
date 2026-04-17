from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import ai_metadata, annotation, embedding_reference, image  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    def create_tables() -> None:
        if settings.auto_create_tables:
            Base.metadata.create_all(bind=engine)

    return app


app = create_app()
