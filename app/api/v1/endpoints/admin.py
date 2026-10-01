from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db
from app.core.config import settings
from app.db.models import GenerationRequestModel, UsageEventModel

router = APIRouter()

@router.get("/admin/metrics")
def get_metrics(db: Session = Depends(get_db)):
    total_requests = db.query(func.count(GenerationRequestModel.id)).scalar() or 0
    succeeded_count = db.query(func.count(GenerationRequestModel.id)).filter(GenerationRequestModel.status == "succeeded").scalar() or 0
    failed_count = db.query(func.count(GenerationRequestModel.id)).filter(GenerationRequestModel.status == "failed").scalar() or 0
    total_cost_usd = db.query(func.sum(GenerationRequestModel.cost_usd)).scalar() or 0.0
    avg_duration_ms = db.query(func.avg(UsageEventModel.duration_ms)).scalar() or 0.0

    return {
        "status": "ok",
        "model": settings.OPENAI_IMAGE_MODEL,
        "quality": settings.OPENAI_IMAGE_QUALITY,
        "storage_type": settings.STORAGE_TYPE,
        "rate_limit_per_day": settings.RATE_LIMIT_PER_DAY,
        "telemetry": {
            "total_requests": total_requests,
            "succeeded_count": succeeded_count,
            "failed_count": failed_count,
            "total_cost_usd": round(float(total_cost_usd), 4),
            "total_cost_formatted": f"${total_cost_usd:.4f} USD",
            "average_duration_ms": round(float(avg_duration_ms), 1),
        },
    }
