import io
import re
from datetime import datetime, UTC
from unittest.mock import patch

import httpx
import pytest

from confereantes.i18n import locale, translate, EN
from confereantes.main import app, CSRF_TOKEN
from confereantes.models import HistoryEntry
from confereantes.risk_engine import analyze
from confereantes.local_ai import explain


@pytest.mark.parametrize("language,heading", [("pt", "O que você recebeu?"), ("en", "What did you receive?")])
def test_language_switch_and_cookie(language, heading):
    import asyncio
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.get("/?lang=" + language)
            assert response.headers["content-language"] == language
            assert heading in response.text
            assert client.cookies.get("lang") == language
            assert heading in (await client.get("/")).text
    asyncio.run(run())


def test_english_report_and_errors_preserve_evidence():
    import asyncio
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver", headers={"Accept-Language": "en", "X-ConfereAntes-CSRF": CSRF_TOKEN}) as client:
            response = await client.post("/analisar", data={"received_text": "Pay now and send the verification code.", "original_text": "R$ 1850,00", "expected_recipient": "Loja João", "displayed_recipient": "Different Name"})
            visible = re.sub(r"<[^>]+>", "", response.text)
            assert "Level: High" in visible
            assert "Request for a password or verification code" in visible
            assert "Significant" in visible or "significant warning signs" in visible
            assert "Loja João" in response.text
            assert "Pedido de senha" not in visible
            empty = await client.post("/analisar", data={})
            assert "Provide at least one" in re.sub(r"<[^>]+>", "", empty.text)
            invalid = await client.post("/api/qr", files={"image": ("bad.png", b"bad", "image/png")})
            assert invalid.json()["error"] == "The file is not a valid image."
    asyncio.run(run())


def test_saved_portuguese_findings_render_in_english():
    import asyncio
    result = analyze(received_text="Faça Pix agora e envie o código de verificação.")
    entry = HistoryEntry(1, datetime.now(UTC), result.level, result.score, result.summary, result.findings, "Texto original não traduzido", "Mensagem original")
    async def run():
        with patch("confereantes.main.get_history_store") as store:
            store.return_value.list.return_value = [entry]
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
                response = await client.get("/historico?lang=en")
                assert "Request for a password or verification code" in response.text
                assert "Texto original não traduzido" in response.text
                assert "Clear history" in response.text
    asyncio.run(run())


def test_generated_explanation_requests_english_without_raw_evidence():
    import json
    requests = []
    def respond(request):
        requests.append(request)
        return httpx.Response(200, json={} if request.url.path == "/api/show" else {"response": json.dumps({"explicacao": "Verify the request through an official channel."})})
    client = httpx.Client(base_url="http://127.0.0.1:11434", transport=httpx.MockTransport(respond))
    token = locale.set("en")
    try:
        with patch("confereantes.local_ai.httpx.Client", return_value=client):
            text, _ = explain(analyze(received_text="Pay now. Private name 987654."))
        payload = json.loads(requests[-1].content)
        assert "Write in English" in payload["system"]
        assert "Pressure or urgency" in payload["prompt"]
        assert '"level": "Caution"' in payload["prompt"]
        assert "987654" not in payload["prompt"]
        assert text.startswith("Verify")
    finally:
        locale.reset(token)


def test_english_known_is_not_now():
    assert analyze(received_text="A known recipient will collect the payment.").score == 0


def test_model_failure_is_localized_and_names_are_not_translated():
    import asyncio
    from confereantes.local_ai import LocalAIUnavailable
    async def run():
        with patch("confereantes.main.explain", side_effect=LocalAIUnavailable("A explicação da IA ficou incompleta e foi descartada.")):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver", headers={"X-ConfereAntes-CSRF": CSRF_TOKEN}) as client:
                response = await client.post("/analisar", data={"received_text": "Pay now", "use_ai": "1", "language": "en"})
                assert "The model explanation was incomplete and was discarded." in response.text
    asyncio.run(run())
    token = locale.set("en")
    try:
        text = 'O nome esperado ("Loja código Pix") difere do nome exibido no aplicativo do banco ("José").'
        assert translate(text) == 'The expected name ("Loja código Pix") differs from the name shown in the banking app ("José").'
    finally:
        locale.reset(token)


def test_catalog_covers_all_static_template_messages():
    from pathlib import Path
    for template in Path("src/confereantes/templates").glob("*.html"):
        for literal in re.findall(r'{{ t\("([^"]+)"\) }}', template.read_text(encoding="utf-8")):
            assert literal in EN, literal
