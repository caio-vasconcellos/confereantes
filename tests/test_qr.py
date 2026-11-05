import io
import unittest

import qrcode
from PIL import Image

from confereantes.qr import decode_qr
from confereantes.ocr import OCRInputError


class QRTests(unittest.TestCase):
    def test_decodes_content_without_opening_it(self):
        payload = "https://exemplo.invalid/pagamento"
        image = qrcode.make(payload)
        output = io.BytesIO()
        image.save(output, format="PNG")
        self.assertEqual(decode_qr(output.getvalue(), content_type="image/png"), [payload])

    def test_blank_image_has_no_codes(self):
        output = io.BytesIO()
        Image.new("RGB", (200, 200), "white").save(output, format="PNG")
        self.assertEqual(decode_qr(output.getvalue()), [])

    def test_rejects_invalid_image(self):
        with self.assertRaises(OCRInputError):
            decode_qr(b"not-an-image", content_type="image/png")
