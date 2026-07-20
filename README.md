# Retail Data Pipeline

Enterprise-grade retail analytics platform with ETL orchestration, interactive dashboard, AI insights, and data services.

## Overview

This project demonstrates a complete retail data pipeline, including data ingestion, transformation, storage, analytics, and visualization.

Key capabilities:
- ETL pipeline for retail sales and inventory data
- FastAPI backend with REST and WebSocket APIs
- Interactive dashboard with real-time analytics and KPI summaries
- Machine learning forecasting and AI insights
- Docker-friendly deployment and local startup scripts

## Features

- Executive dashboard with revenue, profit, orders, and customer intelligence
- Data exploration pages for sales, revenue, customers, inventory, finance, and forecasting
- AI-generated insights and notifications for business decision support
- Exportable sales data and live state updates
- Clean architecture with `api/`, `etl/`, `ml/`, and `data/` folders

## Tech Stack

- Python 3.x
- FastAPI
- SQLAlchemy / Async DB access
- WebSockets for live updates
- Chart.js for interactive analytics
- Docker support for containerized deployment

## Getting Started

### Prerequisites

- Python 3.10+ installed
- `pip` package manager
- Optional: Docker for containerized deployment

### Install dependencies

```powershell
cd c:\Users\Lenovo\Desktop\retail-data-pipeline
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run locally

```powershell
python main.py
```

Open your browser at `http://127.0.0.1:8000` to access the dashboard.

## Dashboard

The dashboard provides:
- High-impact KPI cards with growth trends
- Revenue and profit charts
- Sales analytics and product insights
- AI insights panel with recommended actions
- Interactive filtering, quick actions, and toast notifications

## API Endpoints

- `GET /api/health` — health check
- `GET /api/dashboard` — KPI summary API
- `GET /api/summary` — dashboard summary data
- `GET /api/sales` — sales summary endpoint
- `GET /api/revenue` — revenue time series data
- `GET /api/inventory` — inventory analytics
- `GET /api/finance` — finance metrics
- `GET /api/forecast` — forecasting payload
- `GET /api/ai-insights?q=<query>` — AI insights query

## Project Structure

- `api/` — backend API routes, auth, database, services
- `etl/` — extraction, transformation, load, dashboard summary
- `dashboard/` — UI assets for the analytics dashboard
- `ml/` — training and prediction logic
- `data/` — raw and processed datasets
- `tests/` — automated tests and smoke checks

## Notes

- The dashboard is intentionally designed for local development and demonstration.
- Use `data/sales.csv` as the sample dataset for ETL experiments.
- Extend the dashboard by adding new API routes and chart dashboards.

---

For enhancements, refer to the `api/`, `etl/`, and `dashboard/` modules.
