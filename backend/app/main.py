from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import uuid
import time

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import GreenOpsException
from app.db.base import Base
from app.db.session import engine
from app.api.routes import health

setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # In local development mode with sqlite, create tables if not present; in production, Alembic handles migrations.
    if settings.ENVIRONMENT == "development" and settings.DATABASE_URL.startswith("sqlite"):
        logger.info("Initializing database schemas for local development...", db_url=settings.DATABASE_URL.split("@")[-1])
        Base.metadata.create_all(bind=engine)
    else:
        logger.info("Running in production/managed mode. Database schema evolution managed via Alembic migrations.")
    logger.info("GreenOps backend server started successfully.", version="0.1.0")
    yield
    logger.info("Shutting down GreenOps backend server...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="GreenOps: FinOps & Cloud Carbon Budget Gatekeeper for CI/CD Pipelines",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_and_request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"

    # Don't clutter logs with health checks
    if request.url.path not in ["/healthz", "/ready"]:
        logger.info(
            "HTTP Request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=f"{process_time:.4f}s",
        )
    return response


@app.exception_handler(GreenOpsException)
async def greenops_exception_handler(request: Request, exc: GreenOpsException):
    logger.error("GreenOps Domain Exception", error_message=exc.message, details=exc.details)
    return JSONResponse(
        status_code=400,
        content={"error": exc.__class__.__name__, "message": exc.message, "details": exc.details},
    )


# Include Base Health Routes
app.include_router(health.router)

# Include Domain API Routes
from app.api.routes import webhooks, organizations, repositories, pipelines, sprints, policies, deferred_jobs, dashboard, demo

app.include_router(webhooks.router)
app.include_router(organizations.router)
app.include_router(repositories.router)
app.include_router(pipelines.router)
app.include_router(sprints.router)
app.include_router(policies.router)
app.include_router(deferred_jobs.router)
app.include_router(dashboard.router)
app.include_router(demo.router)

