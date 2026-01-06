"""FastAPI backend for AI-powered quiz platform."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.config import settings
from api.v1 import quizzes

app = FastAPI(
    title="AI Quiz Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Redirect root to quiz listing."""
    return RedirectResponse(url=f"{settings.API_BASE_URL}/quizzes")


@app.get("/health")
async def health():
    """Health check endpoint for Fly.io."""
    return {"status": "ok"}


# Include v1 routers
app.include_router(
    quizzes.router,
    prefix=f"{settings.API_BASE_URL}/quizzes",
    tags=["quizzes"]
)
