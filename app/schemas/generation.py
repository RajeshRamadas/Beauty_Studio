from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class GenerationAcceptedResponse(BaseModel):
    request_id: str
    status: str = "queued"
    category: str
    created_at: str
    status_url: str

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
