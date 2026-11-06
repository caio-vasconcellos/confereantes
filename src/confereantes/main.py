from __future__ import annotations

from functools import lru_cache
from dataclasses import asdict, replace
from datetime import datetime
import secrets
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, Request, UploadFile, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
import httpx
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .history import HistoryStore
from .ocr import MAX_IMAGE_BYTES, OCRInputError, OCRUnavailableError, extract_text, ocr_status
from .risk_engine import analyze
from .models import AnalysisResult, Finding, HistoryEntry
from .qr import decode_qr
from .local_ai import explain, LocalAIUnavailable
from .services import api_enabled, api_request, service_token


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
    version="1.2.0",
    docs_url=None,
    redoc_url=None,
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])
app.add_middleware(SecurityHeadersMiddleware)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
CSRF_TOKEN = secrets.token_urlsafe(32)
templates.env.globals["csrf_token"] = CSRF_TOKEN


def check_browser_token(request: Request, form_token: str = "") -> None:
    supplied = request.headers.get("X-ConfereAntes-CSRF", "") or form_token
    if not secrets.compare_digest(supplied.encode("utf-8"), CSRF_TOKEN.encode("utf-8")):
        raise HTTPException(403, "Reabra a página antes de enviar. Token do formulário inválido.")


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
    use_ai: Annotated[str, Form()] = "",
    csrf_token: Annotated[str, Form()] = "",
    original_image: Annotated[UploadFile | None, File()] = None,
    received_image: Annotated[UploadFile | None, File()] = None,
) -> HTMLResponse:
    check_browser_token(request, csrf_token)
    values: dict[str, str | bool] = {
        "original_text": original_text.strip(),
        "received_text": received_text.strip(),
        "link": link.strip(),
        "pix": pix.strip(),
        "expected_recipient": expected_recipient.strip(),
        "displayed_recipient": displayed_recipient.strip(),
        "save_history": bool(save_history),
        "use_ai": bool(use_ai),
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

    # Aplica os mesmos limites aos textos extraídos das imagens.
    errors.extend(error for error in _validate_values(values) if error not in errors)

    if not values["original_text"] and not values["received_text"] and not values["link"] and not values["pix"]:
        errors.append("Informe pelo menos um texto, uma imagem, um link ou um código Pix.")

    result = None
    history_saved = False
    if not errors:
        payload = dict(
            original_text=str(values["original_text"]),
            received_text=str(values["received_text"]),
            link=str(values["link"]),
            pix=str(values["pix"]),
            expected_recipient=str(values["expected_recipient"]),
            displayed_recipient=str(values["displayed_recipient"]),
        )
        if api_enabled():
            try:
                data = await api_request("POST", "/analises", {**payload, "save_history": bool(save_history), "explain": bool(use_ai)})
                result = _result_from_dict(data)
                history_saved = bool(save_history)
            except (httpx.HTTPError, RuntimeError):
                errors.append("A API C# local está indisponível. Reinicie pelo modo completo.")
        else:
            result = await run_in_threadpool(_process, payload, bool(use_ai))
            if values["save_history"]:
                get_history_store().save(result, original_text=payload["original_text"], received_text=payload["received_text"])
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
async def run_ocr(request: Request, image: Annotated[UploadFile, File()]) -> JSONResponse:
    check_browser_token(request)
    text, message = await _extract_upload(image)
    if not text:
        return JSONResponse({"ok": False, "error": message}, status_code=422)
    return JSONResponse({"ok": True, "text": text, "message": message})


@app.get("/historico", response_class=HTMLResponse)
async def history(request: Request) -> HTMLResponse:
    if api_enabled():
        try:
            data = await api_request("GET", "/historico")
            entries = [HistoryEntry(**{**item, "created_at": datetime.fromisoformat(item["created_at"]), "findings": [Finding(**f) for f in item["findings"]]}) for item in data]
        except (httpx.HTTPError, RuntimeError) as exc:
            raise HTTPException(503, "API C# indisponível. O histórico não foi alterado.") from exc
    else:
        entries = get_history_store().list()
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={"entries": entries},
    )


@app.post("/historico/limpar")
async def clear_history(request: Request, csrf_token: Annotated[str, Form()] = "") -> RedirectResponse:
    check_browser_token(request, csrf_token)
    if api_enabled():
        try:
            await api_request("DELETE", "/historico")
        except (httpx.HTTPError, RuntimeError) as exc:
            raise HTTPException(503, "API C# indisponível. O histórico não foi alterado.") from exc
    else:
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
        result = await run_in_threadpool(extract_text, data, content_type=upload.content_type or "")
    except (OCRInputError, OCRUnavailableError) as exc:
        return "", str(exc)
    finally:
        await upload.close()
    return result.text, "Texto extraído localmente da imagem. Revise antes de confiar."


class AnalysisInput(BaseModel):
    original_text: str = Field(default="", max_length=MAX_TEXT_LENGTH)
    received_text: str = Field(default="", max_length=MAX_TEXT_LENGTH)
    link: str = Field(default="", max_length=MAX_SHORT_LENGTH)
    pix: str = Field(default="", max_length=MAX_SHORT_LENGTH)
    expected_recipient: str = Field(default="", max_length=MAX_SHORT_LENGTH)
    displayed_recipient: str = Field(default="", max_length=MAX_SHORT_LENGTH)
    explain: bool = False


def _process(payload: dict, use_ai: bool) -> AnalysisResult:
    result = analyze(**payload)
    if use_ai:
        try:
            text, model = explain(result)
            result = replace(result, explanation=text, explanation_model=model)
        except LocalAIUnavailable as exc:
            result = replace(result, explanation_error=str(exc))
    return result


def _result_from_dict(data: dict) -> AnalysisResult:
    return AnalysisResult(
        score=data["score"], level=data["level"], findings=[Finding(**item) for item in data["findings"]],
        explanation=data.get("explanation"), explanation_model=data.get("explanation_model"), explanation_error=data.get("explanation_error"),
    )


@app.post("/api/analisar")
async def process_for_api(request: Request, payload: AnalysisInput):
    token = service_token()
    if not token or not secrets.compare_digest(request.headers.get("X-ConfereAntes-Token", "").encode("utf-8"), token.encode("utf-8")):
        raise HTTPException(401, "Acesso interno não autorizado.")
    data = payload.model_dump(exclude={"explain"})
    if not any(data[name].strip() for name in ("original_text", "received_text", "link", "pix")):
        raise HTTPException(422, "Informe pelo menos uma evidência.")
    result = await run_in_threadpool(_process, data, payload.explain)
    return {**asdict(result), "summary": result.summary}


@app.post("/api/qr")
async def read_qr(request: Request, image: Annotated[UploadFile, File()]):
    check_browser_token(request)
    try:
        data = await image.read(MAX_IMAGE_BYTES + 1)
        codes = await run_in_threadpool(decode_qr, data, content_type=image.content_type or "")
        if not codes:
            raise OCRInputError("Nenhum QR Code legível foi encontrado.")
        if len(codes) != 1:
            raise OCRInputError("A imagem contém vários QR Codes. Recorte apenas o que deseja conferir.")
        text = codes[0]
        if len(text) > MAX_SHORT_LENGTH:
            raise OCRInputError("O conteúdo do QR Code excede 2.000 caracteres.")
        return {"ok": True, "text": text, "kind": "pix" if text.startswith("000201") else "link"}
    except ImportError:
        return JSONResponse({"ok": False, "error": 'Instale o suporte QR com pip install -e ".[ocr]".'}, status_code=503)
    except OCRInputError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=422)
    finally:
        await image.close()
