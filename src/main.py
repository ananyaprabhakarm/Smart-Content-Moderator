from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import init_db
from api import text_moderation, image_moderation, summary, analytics

# Initialize FastAPI app
app = FastAPI(
    title="Smart Content Moderator",
    description="Content moderation service that analyzes text and images for inappropriate material",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(text_moderation.router)
app.include_router(image_moderation.router)
app.include_router(summary.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✓ Database initialized")
    print("✓ Smart Content Moderator API is ready")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Smart Content Moderator",
        "version": "1.0.0",
        "endpoints": {
            "text_moderation": "/api/text/moderate",
            "image_moderation": "/api/image/moderate",
            "summary_by_id": "/api/summary/{request_id}",
            "summary_list": "/api/summary",
            "analytics_summary": "/api/v1/analytics/summary?user=<email>"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected"
    }
