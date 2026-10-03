from fastapi import APIRouter
from app.core.config import settings
from app.schemas.common import HealthResponse
from app.services.provider_adapter import calculate_tier_cost

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health():
    est_cost = calculate_tier_cost(settings.OPENAI_IMAGE_MODEL, settings.OPENAI_IMAGE_QUALITY, "1024x1024")
    return {
        "ok": True,
        "status": "ok",
        "model": settings.OPENAI_IMAGE_MODEL,
        "quality": settings.OPENAI_IMAGE_QUALITY,
        "estimated_cost_per_image": f"~${est_cost:.3f} USD",
        "api_key_configured": bool(settings.OPENAI_API_KEY),
        "demo_mode": settings.DEMO_MODE,
    }

@router.get("/ready")
def ready():
    return {
        "status": "ready",
        "dependencies": {
            "api_key": bool(settings.OPENAI_API_KEY),
            "storage": settings.STORAGE_TYPE,
        }
    }
