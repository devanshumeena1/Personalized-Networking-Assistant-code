import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.models.database import engine, Base
from app.routers import conversation, factcheck, history

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize database tables
try:
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Backend API for theme extraction, conversation starter generation, and fact-checking."
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api prefix
app.include_router(conversation.router, prefix="/api")
app.include_router(factcheck.router, prefix="/api")
app.include_router(history.router, prefix="/api")

# Register routers at root level as well
app.include_router(conversation.router)
app.include_router(factcheck.router)
app.include_router(history.router)

# Mount static files at root
# Note: Mount this after API routers so static wildcard matches don't shadow API routes
app.mount("/", StaticFiles(directory="frontend-static", html=True), name="static")
