from typing import Optional, Any, Dict
from pydantic import BaseModel

class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail

class HealthResponse(BaseModel):
    ok: bool
    status: str = "ok"
    model: str
    quality: str
    estimated_cost_per_image: str
    api_key_configured: bool
