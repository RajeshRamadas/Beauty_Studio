"""Entry point kept for `uvicorn main:app`.

The application lives in app/main.py; this module re-exports it so both
`uvicorn main:app` and `uvicorn app.main:app` start the same server.
The earlier single-file prototype (POST /api/transform) is in git history.
"""
from app.main import app  # noqa: F401
