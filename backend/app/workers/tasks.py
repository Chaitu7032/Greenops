import structlog
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.scheduler_service import dispatch_due_deferred_jobs

logger = structlog.get_logger()


@celery_app.task(name="app.workers.tasks.check_and_dispatch_deferred_jobs")
def check_and_dispatch_deferred_jobs():
    """Background task executed periodically by Celery worker to dispatch due deferred CI jobs."""
    logger.info("Executing periodic deferred jobs check...")
    db = SessionLocal()
    try:
        dispatched = dispatch_due_deferred_jobs(db)
        logger.info("Deferred jobs check completed", dispatched_count=len(dispatched))
        return {"status": "success", "dispatched_count": len(dispatched)}
    except Exception as e:
        logger.error("Error in periodic deferred jobs check", error=str(e))
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
