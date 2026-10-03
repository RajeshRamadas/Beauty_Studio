from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class GenerationAcceptedResponse(BaseModel):
    request_id: str
    status: str = "queued"
    category: str
    created_at: str
    status_url: str
    enhancements: List[str] = Field([], description="Automatic corrections applied to the user's photo")

class ImageAssetInfo(BaseModel):
    id: str
    role: str
    mime_type: str
    byte_size: int
    width: int
    height: int
    url: str

class GenerationStatusResponse(BaseModel):
    request_id: str
    status: str  # 'queued', 'processing', 'succeeded', 'failed'
    category: str
    model: Optional[str] = None
    quality: Optional[str] = None
    size: Optional[str] = None
    cost_usd: Optional[float] = None
    cost_formatted: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    result_image_b64: Optional[str] = None
    assets: List[ImageAssetInfo] = []
    accuracy: Optional[int] = Field(None, description="AI-estimated accuracy 0-100 (lowest of the criteria)")
    accuracy_breakdown: Optional[Dict[str, int]] = None
    attempts: Optional[int] = None
    selections: List[Dict[str, Any]] = Field([], description="Per area: template ID and version, custom style or reference photo")
    intensity: Optional[str] = None

class GenerationResponse(BaseModel):
    request_id: str
    status: str = "succeeded"
    category: str
    model: str
    quality: str
    size: str
    cost_usd: float
    cost_formatted: str
    is_exact_cost: bool
    usage: Optional[Dict[str, Any]] = None
    image: str = Field(..., description="Base64 encoded PNG image data")
