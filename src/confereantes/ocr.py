from __future__ import annotations

import io
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import version


MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/webp"}


class OCRInputError(ValueError):
    """Imagem rejeitada antes da execução do OCR."""


class OCRUnavailableError(RuntimeError):
    """OCR local não está instalado ou configurado."""


@dataclass(frozen=True, slots=True)
class OCRResult:
    text: str
    language: str


def extract_text(data: bytes, *, content_type: str = "", language: str = "pt") -> OCRResult:
    if not data:
        raise OCRInputError("A imagem está vazia.")
    if len(data) > MAX_IMAGE_BYTES:
        raise OCRInputError("A imagem excede o limite de 8 MB.")
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise OCRInputError("Use uma imagem PNG, JPG ou WEBP.")

    try:
        from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError
    except ImportError as exc:
        raise OCRUnavailableError('Instale o suporte OCR com: pip install -e ".[ocr]"') from exc

    try:
        with Image.open(io.BytesIO(data)) as source:
            source.verify()
        with Image.open(io.BytesIO(data)) as source:
            width, height = source.size
            if width * height > MAX_IMAGE_PIXELS:
                raise OCRInputError("A imagem tem resolução acima do limite permitido.")
            image = ImageOps.exif_transpose(source).convert("L")
            image = ImageEnhance.Contrast(image).enhance(1.35)
            if image.width < 1400:
                scale = min(2.0, 1400 / max(1, image.width))
                image = image.resize((round(image.width * scale), round(image.height * scale)))
    except (UnidentifiedImageError, OSError) as exc:
        raise OCRInputError("O arquivo não é uma imagem válida.") from exc

    try:
        result = _get_engine()(image)
        text = "\n".join(result.txts or ())
    except ImportError as exc:
        raise OCRUnavailableError('Instale o suporte OCR com: pip install -e ".[ocr]"') from exc
    except Exception as exc:
        raise OCRUnavailableError("O motor OCR local não conseguiu ler a imagem.") from exc

    cleaned = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if not cleaned:
        raise OCRInputError("Nenhum texto legível foi encontrado na imagem.")
    return OCRResult(text=cleaned, language=language)


def ocr_status() -> tuple[bool, str]:
    try:
        from PIL import Image  # noqa: F401
        import onnxruntime
        import rapidocr  # noqa: F401
    except ImportError:
        return False, "Suporte OCR opcional não instalado."
    return True, f"OCR local disponível (RapidOCR {version('rapidocr')}, ONNX Runtime {onnxruntime.__version__})."


@lru_cache(maxsize=1)
def _get_engine():
    from rapidocr import RapidOCR

    return RapidOCR(
        params={
            "Det.lang_type": "pt",
            "Rec.lang_type": "pt",
        }
    )
