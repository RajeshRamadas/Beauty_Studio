from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/client-config")
def client_config():
    """Public settings the web app needs at start-up.

    Only values that are safe to expose to browsers belong here. The Google Maps
    key is a browser key by design and must be restricted by HTTP referrer.
    """
    key = settings.GOOGLE_MAPS_API_KEY
    return {
        "maps": {
            "provider": "google" if key else "osm",
            "google_api_key": key or None,
            "google_map_id": settings.GOOGLE_MAPS_MAP_ID if key else None,
        }
    }
