"""Decodificação local de QR Code, sem acessar o conteúdo encontrado."""
import io

from .ocr import ALLOWED_CONTENT_TYPES, MAX_IMAGE_BYTES, MAX_IMAGE_PIXELS, OCRInputError


def decode_qr(data: bytes, *, content_type: str = "") -> list[str]:
    from PIL import Image, ImageOps, UnidentifiedImageError
    import zxingcpp

    if not data or len(data) > MAX_IMAGE_BYTES:
        raise OCRInputError("Envie uma imagem de até 8 MB.")
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise OCRInputError("Use uma imagem PNG, JPG ou WEBP.")
    try:
        with Image.open(io.BytesIO(data)) as source:
            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise OCRInputError("A imagem tem resolução acima do limite permitido.")
            image = ImageOps.exif_transpose(source).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise OCRInputError("O arquivo não é uma imagem válida.") from exc
    codes = zxingcpp.read_barcodes(image, formats=zxingcpp.BarcodeFormat.QRCode)
    return list(dict.fromkeys(code.text for code in codes if code.valid and code.text))
