import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from confereantes.ocr import OCRInputError, extract_text


def make_image() -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (300, 100), "white").save(output, format="PNG")
    return output.getvalue()


class OCRTests(unittest.TestCase):
    @patch("confereantes.ocr._get_engine")
    def test_processes_valid_image_in_memory(self, mocked_engine) -> None:
        mocked_engine.return_value.return_value = SimpleNamespace(
            txts=("Pix de R$ 150,00", "Confira o destinatário"),
        )

        result = extract_text(make_image(), content_type="image/png")

        self.assertEqual(result.text, "Pix de R$ 150,00\nConfira o destinatário")
        self.assertEqual(result.language, "pt")

    def test_rejects_unsupported_file_type(self) -> None:
        with self.assertRaisesRegex(OCRInputError, "PNG, JPG ou WEBP"):
            extract_text(make_image(), content_type="application/pdf")

    def test_rejects_invalid_image(self) -> None:
        with self.assertRaisesRegex(OCRInputError, "imagem válida"):
            extract_text(b"nao-e-imagem", content_type="image/png")


if __name__ == "__main__":
    unittest.main()
