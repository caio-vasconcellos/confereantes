import unittest
from unittest.mock import patch, AsyncMock
import os
import io
import qrcode

import httpx

from confereantes.main import app, CSRF_TOKEN
from confereantes.ocr import OCRResult


class WebTests(unittest.IsolatedAsyncioTestCase):
    async def test_plain_form_token_works_without_javascript_header(self):
        response = await self.client.post("/analisar", data={"received_text": "Mensagem de teste", "csrf_token": CSRF_TOKEN}, headers={"X-ConfereAntes-CSRF": "", "origin": "null"})
        self.assertEqual(response.status_code, 200)

    async def test_rejects_cross_site_mutation(self):
        for headers in ({"origin": "https://exemplo.invalid"}, {"sec-fetch-site": "cross-site"}, {"origin": "null"}):
            with self.subTest(headers=headers):
                response = await self.client.post("/historico/limpar", headers={**headers, "X-ConfereAntes-CSRF": ""})
                self.assertEqual(response.status_code, 403)

    async def test_same_origin_form_is_allowed(self):
        response = await self.client.post("/analisar", data={"received_text": "Mensagem de teste"}, headers={"origin": "http://testserver"})
        self.assertEqual(response.status_code, 200)

    async def test_escapes_untrusted_content_in_report(self):
        response = await self.client.post("/analisar", data={"received_text": '<script>alert("teste")</script>', "expected_recipient": "Loja", "displayed_recipient": '<img src=x onerror=alert(1)>'})
        self.assertNotIn('<img src=x onerror=alert(1)>', response.text)
        self.assertIn("&lt;img", response.text)

    async def asyncSetUp(self) -> None:
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
            headers={"X-ConfereAntes-CSRF": CSRF_TOKEN},
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    async def test_home_renders_security_headers(self) -> None:
        response = await self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Confira antes de pagar", response.text)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertIn("default-src 'self'", response.headers["content-security-policy"])

    async def test_requires_at_least_one_evidence(self) -> None:
        response = await self.client.post("/analisar", data={})

        self.assertEqual(response.status_code, 422)
        self.assertIn("Informe pelo menos", response.text)

    async def test_analyzes_form_data(self) -> None:
        response = await self.client.post(
            "/analisar",
            data={"received_text": "Faça o Pix agora e envie o código de verificação."},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nível: Alto", response.text)
        self.assertIn("Pedido de senha ou código", response.text)

    @patch("confereantes.main.extract_text")
    async def test_extracts_uploaded_image_without_persisting_it(self, mocked_extract) -> None:
        mocked_extract.return_value = OCRResult(text="Oferta por R$ 100,00", language="por")
        response = await self.client.post(
            "/api/ocr",
            files={"image": ("oferta.png", b"imagem-ficticia", "image/png")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["text"], "Oferta por R$ 100,00")

    async def test_internal_processor_requires_service_token(self) -> None:
        with patch.dict(os.environ, {"CONFEREANTES_SERVICE_TOKEN": "test-token"}):
            denied = await self.client.post("/api/analisar", json={"received_text": "Envie senha agora"})
            allowed = await self.client.post("/api/analisar", json={"received_text": "Envie senha agora"}, headers={"X-ConfereAntes-Token": "test-token"})
        self.assertEqual(denied.status_code, 401)
        self.assertEqual(allowed.status_code, 200)
        self.assertIn(allowed.json()["level"], {"baixo", "atencao", "alto"})

    async def test_reads_qr_to_reviewable_content(self) -> None:
        output = io.BytesIO()
        qrcode.make("000201-EXEMPLO-TESTE").save(output, format="PNG")
        response = await self.client.post("/api/qr", files={"image": ("teste.png", output.getvalue(), "image/png")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["kind"], "pix")
        self.assertEqual(response.json()["text"], "000201-EXEMPLO-TESTE")

    async def test_complete_mode_routes_to_csharp_api(self) -> None:
        response_data = {"score": 60, "level": "alto", "findings": [], "summary": "Confirme."}
        with patch.dict(os.environ, {"CONFEREANTES_USE_API": "1"}), patch("confereantes.main.api_request", new_callable=AsyncMock, return_value=response_data) as gateway:
            response = await self.client.post("/analisar", data={"received_text": "Pix agora", "save_history": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(gateway.call_args.args[2]["save_history"])
        self.assertIn("Nível: Alto", response.text)


if __name__ == "__main__":
    unittest.main()
