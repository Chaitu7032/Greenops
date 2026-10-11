from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
import redis

from app.api.dependencies import get_db
from app.core.config import settings

router = APIRouter(tags=["Health & Readiness"])


@router.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    """Liveness probe endpoint."""
    return {"status": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check(db: Session = Depends(get_db)):
    """Deep readiness probe verifying DB connection and Redis cache/broker availability."""
    db_ready = False
    redis_ready = False
    errors = []

    # Verify Database
    try:
        db.execute(text("SELECT 1"))
        db_ready = True
    except Exception as e:
        errors.append(f"Database error: {str(e)}")

    # Verify Redis (soft check, does not fail if optional in local mock mode)
    try:
        r = redis.from_url(settings.REDIS_URL, socket_timeout=1.5)
        r.ping()
        redis_ready = True
    except Exception as e:
        errors.append(f"Redis note: {str(e)}")
        redis_ready = False

    is_ready = db_ready

    response_payload = {
        "status": "ready" if is_ready else "degraded",
        "database": db_ready,
        "redis": redis_ready,
        "environment": settings.ENVIRONMENT,
        "errors": errors if errors else None,
    }

    if not is_ready:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=response_payload)

    return response_payload
