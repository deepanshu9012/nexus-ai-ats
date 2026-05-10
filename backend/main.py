import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <-- 1. Import CORS Middleware

from routes import agent, auth, candidates
from routes.router import api_router
from services.qdrant_service import init_collection


if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        init_collection()
    except Exception:
        logger.exception("Qdrant collection initialization failed during startup.")
    yield


def create_application() -> FastAPI:
    app = FastAPI(
        title="ATS Backend",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # <-- 2. Add the CORS Middleware block here
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins for local development
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods (POST, GET, OPTIONS, etc.)
        allow_headers=["*"],  # Allows all headers
    )
    
    app.include_router(api_router)
    app.include_router(agent.router)
    app.include_router(auth.router, tags=["Authentication"])
    app.include_router(candidates.router)
    return app


app = create_application()
