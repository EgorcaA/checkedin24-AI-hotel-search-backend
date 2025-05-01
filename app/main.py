from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import hotels

app = FastAPI(title="Hotel API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hotels.router, prefix="/api", tags=["hotels"])
