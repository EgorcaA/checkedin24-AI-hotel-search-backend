from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .logger import get_logger
from .routers import hotels

logger = get_logger(__name__)

app = FastAPI(title="Hotel API")

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


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Hotel API application")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Hotel API application")


app.include_router(hotels.router, prefix="/api", tags=["hotels"])
