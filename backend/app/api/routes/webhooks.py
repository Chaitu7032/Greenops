import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
import structlog

from app.api.dependencies import get_db
from app.core.config import settings
from app.core.security import verify_github_signature
from app.models.webhook_event import WebhookEvent
from app.schemas.webhook import WebhookProcessingResult
from app.services.webhook_service import process_pull_request_event, process_workflow_run_event

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/webhooks", tags=["GitHub Webhooks"])


@router.post("/github", status_code=status.HTTP_200_OK, response_model=WebhookProcessingResult)
async def handle_github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    x_github_delivery: str = Header(..., alias="X-GitHub-Delivery"),
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
):
    """
    Ingest, authenticate, and process GitHub Pull Request and Workflow Run webhooks.
    """
    body_bytes = await request.body()

    # 1. HMAC-SHA256 Authentication
    # In development mode, if signature is omitted, allow pass-through if secret is default demo
    is_valid = verify_github_signature(body_bytes, settings.GITHUB_WEBHOOK_SECRET, x_hub_signature_256)
    if not is_valid:
        if settings.ENVIRONMENT != "development" or x_hub_signature_256 is not None:
            logger.warning("Invalid webhook HMAC signature", delivery_id=x_github_delivery)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid HMAC-SHA256 signature")

    # 2. Webhook Idempotency Check
    existing_event = db.query(WebhookEvent).filter(WebhookEvent.github_delivery_id == x_github_delivery).first()
    if existing_event:
        logger.info("Duplicate webhook delivery received", delivery_id=x_github_delivery)
        return WebhookProcessingResult(
            status="idempotent_skip",
            message="Webhook delivery already received and processed",
            event_type=x_github_event,
            delivery_id=x_github_delivery,
        )

    # 3. Parse JSON Payload
    try:
        payload = await request.json()
    except Exception as e:
        logger.error("Failed to parse JSON webhook payload", error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed JSON payload")

    payload_hash = hashlib.sha256(body_bytes).hexdigest()

    # 4. Record Webhook Delivery Event
    webhook_event = WebhookEvent(
        github_delivery_id=x_github_delivery,
        event_type=x_github_event,
        payload_hash=payload_hash,
        payload=payload,
        processed=False,
    )
    db.add(webhook_event)
    db.commit()
    db.refresh(webhook_event)

    # 5. Route and Process Event
    pipeline_run_id = None
    policy_decision = None
    reason = None

    try:
        if x_github_event == "pull_request":
            action = payload.get("action")
            if action in ("opened", "synchronize", "reopened"):
                res = process_pull_request_event(db, payload)
                pipeline_run_id = res.get("pipeline_run_id")
                policy_decision = res.get("policy_decision")
                reason = res.get("reason")

        elif x_github_event == "workflow_run":
            action = payload.get("action")
            if action == "completed":
                res = process_workflow_run_event(db, payload)
                pipeline_run_id = res.get("pipeline_run_id")

        webhook_event.processed = True
        webhook_event.processed_at = datetime.now(timezone.utc)
        db.commit()

        return WebhookProcessingResult(
            status="processed",
            message=f"Successfully handled GitHub {x_github_event} event",
            event_type=x_github_event,
            delivery_id=x_github_delivery,
            pipeline_run_id=pipeline_run_id,
            policy_decision=policy_decision,
            reason=reason,
        )

    except Exception as exc:
        logger.error("Error during webhook event processing", error=str(exc), delivery_id=x_github_delivery)
        webhook_event.processed = False
        webhook_event.processing_error = str(exc)
        db.commit()
        return WebhookProcessingResult(
            status="error",
            message=f"Error processing webhook: {str(exc)}",
            event_type=x_github_event,
            delivery_id=x_github_delivery,
        )
