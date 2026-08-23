"""
Lead Manager Microservice FastAPI Main Application.
"""

import asyncio
import sniffio
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from .a2a.agent import a2a_router
from .agents.followup_agent import FollowUpAgent
from .api.routes import router as api_router
from .config.logging import get_logger, setup_logging
from .config.settings import get_settings
from .repository.database import get_db_manager
from .repository.leads import LeadRepository
from .repository.tasks import TaskRepository

setup_logging()
logger = get_logger("Main")

followup_task_handle = None


async def stale_lead_worker():
    settings = get_settings()
    interval = settings.FOLLOWUP_CHECK_INTERVAL_SECONDS
    logger.info(f"Stale lead follow-up worker started (interval: {interval}s)")

    while True:
        try:
            db = get_db_manager()
            agent = FollowUpAgent(
                lead_repo=LeadRepository(db),
                task_repo=TaskRepository(db),
                settings=settings,
            )
            tasks = await agent.scan_and_generate_followup_tasks()
            if tasks:
                logger.info(f"Follow-up scan generated {len(tasks)} tasks.")
        except asyncio.CancelledError:
            logger.info("Stale lead worker cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in stale lead worker: {e}", exc_info=True)

        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    db = get_db_manager()
    await db.init_db()

    global followup_task_handle
    followup_task_handle = asyncio.create_task(stale_lead_worker())

    yield

    if followup_task_handle:
        followup_task_handle.cancel()
        try:
            await followup_task_handle
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="AgencyOS Lead Manager Microservice",
    description="Deterministic Lead Lifecycle Management, A2A Agent, and System of Record.",
    version="1.0.0",
    lifespan=lifespan,
)




class SniffioASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            token = sniffio.current_async_library_cvar.set("asyncio")
            try:
                await self.app(scope, receive, send)
            finally:
                sniffio.current_async_library_cvar.reset(token)
        else:
            await self.app(scope, receive, send)


app.add_middleware(SniffioASGIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(a2a_router)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy", "service": "lead_manager", "port": 8082}


@app.get("/ready", status_code=status.HTTP_200_OK)
async def ready_check():
    return {"status": "ready", "database": "connected"}
