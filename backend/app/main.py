"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base
from .routes import auth_router, users_router, templates_router, contracts_router

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Contract Management System API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Create database tables on startup"""
    Base.metadata.create_all(bind=engine)


# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(templates_router, prefix="/api/v1")
app.include_router(contracts_router, prefix="/api/v1")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Contract Management System API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
