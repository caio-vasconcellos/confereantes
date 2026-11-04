import unittest
from unittest.mock import patch

import httpx

from confereantes.main import app
from confereantes.ocr import OCRResult


class WebTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
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


if __name__ == "__main__":
    unittest.main()
