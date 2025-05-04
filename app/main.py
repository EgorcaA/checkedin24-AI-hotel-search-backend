from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .logger import get_logger
from .routers import hotels

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Hotel API application")
    yield
    # Shutdown
    logger.info("Shutting down Hotel API application")


app = FastAPI(title="Hotel API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:5173",  # Vite's default development port
        "http://localhost:3000",
        "https://checkedin24-aihotelsearch.vercel.app",  # Remove trailing slash
        "*",  # Allow all origins temporarily for development
    ],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(hotels.router, prefix="/api", tags=["hotels"])
