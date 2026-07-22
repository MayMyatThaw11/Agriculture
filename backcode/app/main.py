from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import router
from app.core.config import get_settings
from app.seed import init_database


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_database()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version=__version__, debug=settings.debug, lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router, prefix=settings.api_prefix)
    # The current React client defaults to /api; keep that shorthand compatible
    # while the documented/versioned contract remains /api/v1.
    if settings.api_prefix != "/api":
        application.include_router(router, prefix="/api", include_in_schema=False)

    @application.get("/health", include_in_schema=False)
    def liveness() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_app()
