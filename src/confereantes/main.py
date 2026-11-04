from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .history import HistoryStore
from .ocr import MAX_IMAGE_BYTES, OCRInputError, OCRUnavailableError, extract_text, ocr_status
from .risk_engine import analyze


BASE_DIR = Path(__file__).resolve().parent
MAX_TEXT_LENGTH = 30_000
MAX_SHORT_LENGTH = 2_000
OCR_AVAILABLE, OCR_STATUS = ocr_status()


class SecurityHeadersMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        async def send_with_headers(message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend(
                    [
                        (b"cache-control", b"no-store"),
                        (b"x-content-type-options", b"nosniff"),
                        (b"referrer-policy", b"no-referrer"),
                        (
                            b"content-security-policy",
                            b"default-src 'self'; style-src 'self'; script-src 'self'; "
                            b"img-src 'self' data: blob:; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
                        ),
                    ]
                )
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)

app = FastAPI(
    title="ConfereAntes",
    description="Análise local e explicável de sinais de risco.",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])
app.add_middleware(SecurityHeadersMiddleware)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@lru_cache(maxsize=1)
def get_history_store() -> HistoryStore:
    return HistoryStore()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "result": None,
            "values": {},
            "messages": [],
            "errors": [],
            "ocr_available": OCR_AVAILABLE,
            "ocr_status": OCR_STATUS,
            "history_saved": False,
        },
    )


@app.post("/analisar", response_class=HTMLResponse)
async def run_analysis(
    request: Request,
    original_text: Annotated[str, Form()] = "",
    received_text: Annotated[str, Form()] = "",
    link: Annotated[str, Form()] = "",
    pix: Annotated[str, Form()] = "",
    expected_recipient: Annotated[str, Form()] = "",
    displayed_recipient: Annotated[str, Form()] = "",
    save_history: Annotated[str, Form()] = "",
    original_image: Annotated[UploadFile | None, File()] = None,
    received_image: Annotated[UploadFile | None, File()] = None,
) -> HTMLResponse:
    values: dict[str, str | bool] = {
        "original_text": original_text.strip(),
        "received_text": received_text.strip(),
        "link": link.strip(),
        "pix": pix.strip(),
        "expected_recipient": expected_recipient.strip(),
        "displayed_recipient": displayed_recipient.strip(),
        "save_history": bool(save_history),
    }
    errors = _validate_values(values)
    messages: list[str] = []

    if not values["original_text"] and original_image and original_image.filename:
        text, message = await _extract_upload(original_image)
        values["original_text"] = text
        (errors if not text else messages).append(message)

    if not values["received_text"] and received_image and received_image.filename:
        text, message = await _extract_upload(received_image)
        values["received_text"] = text
        (errors if not text else messages).append(message)

    if not values["original_text"] and not values["received_text"] and not values["link"] and not values["pix"]:
        errors.append("Informe pelo menos um texto, uma imagem, um link ou um código Pix.")

    result = None
    history_saved = False
    if not errors:
        result = analyze(
            original_text=str(values["original_text"]),
            received_text=str(values["received_text"]),
            link=str(values["link"]),
            pix=str(values["pix"]),
            expected_recipient=str(values["expected_recipient"]),
            displayed_recipient=str(values["displayed_recipient"]),
        )
        if values["save_history"]:
            get_history_store().save(
                result,
                original_text=str(values["original_text"]),
                received_text=str(values["received_text"]),
            )
            history_saved = True

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "result": result,
            "values": values,
            "messages": messages,
            "errors": errors,
            "ocr_available": OCR_AVAILABLE,
            "ocr_status": OCR_STATUS,
            "history_saved": history_saved,
        },
        status_code=422 if errors else 200,
    )


@app.post("/api/ocr")
async def run_ocr(image: Annotated[UploadFile, File()]) -> JSONResponse:
    text, message = await _extract_upload(image)
    if not text:
        return JSONResponse({"ok": False, "error": message}, status_code=422)
    return JSONResponse({"ok": True, "text": text, "message": message})


@app.get("/historico", response_class=HTMLResponse)
async def history(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={"entries": get_history_store().list()},
    )


@app.post("/historico/limpar")
async def clear_history() -> RedirectResponse:
    get_history_store().clear()
    return RedirectResponse(url="/historico?limpo=1", status_code=303)


@app.get("/saude")
async def health() -> dict[str, str | bool]:
    return {"status": "ok", "ocr_available": OCR_AVAILABLE, "ocr_status": OCR_STATUS}


def _validate_values(values: dict[str, str | bool]) -> list[str]:
    errors: list[str] = []
    for name in ("original_text", "received_text"):
        if len(str(values[name])) > MAX_TEXT_LENGTH:
            errors.append("Cada campo de texto deve ter no máximo 30.000 caracteres.")
            break
    for name in ("link", "pix", "expected_recipient", "displayed_recipient"):
        if len(str(values[name])) > MAX_SHORT_LENGTH:
            errors.append("Link, Pix e nomes devem ter no máximo 2.000 caracteres.")
            break
    return errors


async def _extract_upload(upload: UploadFile) -> tuple[str, str]:
    try:
        data = await upload.read(MAX_IMAGE_BYTES + 1)
        result = extract_text(data, content_type=upload.content_type or "")
    except (OCRInputError, OCRUnavailableError) as exc:
        return "", str(exc)
    finally:
        await upload.close()
    return result.text, "Texto extraído localmente da imagem. Revise antes de confiar."
