import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import init_indexes, close_client
from app.routes.health import router as health_router
from app.routes.events import router as events_router
from app.routes.logs import router as logs_router
from app.routes.parser_studio import router as parser_studio_router
from app.routes.parsers import router as parsers_router
from app.routes.sources import router as sources_router
from app.routes.dashboard import router as dashboard_router
from app.routes.demo import router as demo_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ulpf.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure indexes
    logger.info("Starting up %s (version %s)...", settings.PROJECT_NAME, settings.VERSION)
    init_indexes()
    yield
    # Shutdown: clean up DB client
    logger.info("Shutting down %s...", settings.PROJECT_NAME)
    close_client()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Universal Log Pre-processing Framework — SIH 2026 NTRO Solution",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for prototype development ease
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler for resilience
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error processing request %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "An unexpected server error occurred.", "error": str(exc)}
    )

# Include routes under /api
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(events_router, prefix=settings.API_V1_PREFIX)
app.include_router(logs_router, prefix=settings.API_V1_PREFIX)
app.include_router(parser_studio_router, prefix=settings.API_V1_PREFIX)
app.include_router(parsers_router, prefix=settings.API_V1_PREFIX)
app.include_router(sources_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(demo_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "framework": "ULPF — Universal Log Pre-processing Framework",
        "documentation": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
