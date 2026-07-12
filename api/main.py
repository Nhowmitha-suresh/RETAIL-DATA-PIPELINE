from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import HTMLResponse

from etl.pipeline import ensure_dataset, get_dashboard_summary, predict_sales, train_model

app = FastAPI(title="Retail Intelligence Platform", version="1.0.0")
app.mount("/static", StaticFiles(directory="dashboard"), name="static")

templates = Jinja2Templates(directory="dashboard")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    summary = get_dashboard_summary()
    return templates.TemplateResponse("index.html", {"request": request, "summary": summary})


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "message": "Retail pipeline is running"}


@app.get("/api/summary")
async def summary() -> dict:
    return get_dashboard_summary()


@app.post("/api/predict")
async def predict(payload: dict) -> dict:
    return predict_sales(payload)


@app.post("/api/train")
async def train() -> dict:
    return train_model(df=ensure_dataset())
