from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .risk_engine import analyze


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="ConfereAntes",
    description="Análise local e explicável de sinais de risco.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"result": None, "values": {}},
    )


@app.post("/analisar", response_class=HTMLResponse)
async def run_analysis(
    request: Request,
    original_text: str = Form(default=""),
    received_text: str = Form(default=""),
    link: str = Form(default=""),
    pix: str = Form(default=""),
) -> HTMLResponse:
    values = {
        "original_text": original_text,
        "received_text": received_text,
        "link": link,
        "pix": pix,
    }
    result = analyze(**values)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"result": result, "values": values},
    )


@app.get("/saude")
async def health() -> dict[str, str]:
    return {"status": "ok"}

