"""Main FastAPI application entrypoint for the Communication Service."""
import logging
import os
import sys
from contextlib import asynccontextmanager

# Ensure service directory is in sys.path when launched from any directory
_service_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _service_dir not in sys.path:
    sys.path.insert(0, _service_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import get_settings
from app.events.bus import event_bus
from app.events.dispatcher import event_dispatcher
from app.imap.listener import imap_listener
from app.persistence.database import db
from app.responder.engine import auto_responder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("communication_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Initializing Communication Service (Port %s)...", settings.PORT)

    # 1. Initialize database schema
    await db.init_db()
    logger.info("Database schema initialized at '%s'.", settings.DATABASE_PATH)

    # 2. Subscribe dispatcher and auto-responder to event bus
    event_bus.subscribe("*", event_dispatcher.handle_event)
    event_bus.subscribe("email.received", auto_responder.handle_new_inbound)
    await event_bus.start()

    # 3. Start IMAP listener background worker
    await imap_listener.start()

    yield

    # Shutdown
    logger.info("Shutting down Communication Service...")
    await imap_listener.stop()
    await event_bus.stop()
    logger.info("Communication Service shutdown complete.")


app = FastAPI(
    title="AgencyOS Communication Service",
    description="Zero-cloud Gmail IMAP IDLE and SMTP communication microservice for AgencyOS.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST and A2A routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    )
