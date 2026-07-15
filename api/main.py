from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import HTMLResponse

from etl.pipeline import ensure_dataset, get_dashboard_summary, predict_sales, train_model
from .routes import router as api_router
from .ws import router as ws_router
import logging
from fastapi.responses import JSONResponse
from fastapi import Request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('retail')
from . import db

app = FastAPI(
    title="Retail Intelligence Platform",
    version="1.0.0",
    description="Enterprise retail analytics backend with CRUD APIs, AI insights, and live WebSocket updates.",
    contact={"name": "Retail API Support", "email": "support@example.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)
app.mount("/static", StaticFiles(directory="dashboard"), name="static")

templates = Jinja2Templates(directory="dashboard")

# Include modular API routes
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    summary = get_dashboard_summary()
    return templates.TemplateResponse(request, "index.html", {"summary": summary})


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "message": "Retail pipeline is running"}


@app.on_event("startup")
async def startup_event():
    # Eagerly ensure dataset exists (keeps backward compatibility)
    ensure_dataset()
    # Create local SQLite schema when PostgreSQL is not configured
    try:
        await db.create_schema()
    except Exception:
        pass


@app.on_event("shutdown")
async def shutdown_event():
    # Close DB engine on shutdown
    await db.engine.dispose()


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception('Unhandled error: %s', exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
