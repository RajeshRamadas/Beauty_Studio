import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine

setup_logging()

# Auto-create tables for development
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

logging.getLogger(__name__).info(
    "Salon map provider: %s",
    "Google Maps (GOOGLE_MAPS_API_KEY is set)" if settings.GOOGLE_MAPS_API_KEY
    else "OpenStreetMap (set GOOGLE_MAPS_API_KEY to use Google Maps)",
)

@app.get("/", include_in_schema=False)
def index():
    return FileResponse("index.html")

@app.get("/health", include_in_schema=False)
def health_legacy():
    from app.api.v1.endpoints.health import health as h
    return h()

@app.get("/{filename}", include_in_schema=False)
def serve_root_files(filename: str):
    import os
    from fastapi import HTTPException
    allowed_exts = (".jpg", ".jpeg", ".png", ".webp", ".css", ".js")
    if any(filename.endswith(ext) for ext in allowed_exts) and os.path.exists(filename):
        return FileResponse(filename)
    raise HTTPException(status_code=404, detail="File not found")



