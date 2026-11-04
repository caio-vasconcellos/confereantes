from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


class PixPayloadError(ValueError):
    """Indica que um Pix copia e cola não segue a estrutura EMV esperada."""


@dataclass(frozen=True, slots=True)
class PixPayload:
    merchant_name: str = ""
    merchant_city: str = ""
    amount: Decimal | None = None
    key: str = ""
    txid: str = ""
    crc_valid: bool = False


def parse_pix_payload(raw: str) -> PixPayload:
    value = raw.strip().replace("\r", "").replace("\n", "")
    if not value.startswith("000201"):
        raise PixPayloadError("O conteúdo não começa como um Pix copia e cola.")

    fields = _parse_tlv(value)
    crc_value = fields.get("63", "")
    if len(crc_value) != 4:
        raise PixPayloadError("O código não possui um CRC válido no final.")

    crc_prefix = value[: value.rfind("6304") + 4]
    crc_valid = _crc16_ccitt(crc_prefix.encode("utf-8")) == crc_value.upper()

    merchant_account = {}
    for tag in ("26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51"):
        if tag in fields:
            try:
                candidate = _parse_tlv(fields[tag])
            except PixPayloadError:
                continue
            if candidate.get("00", "").lower() == "br.gov.bcb.pix":
                merchant_account = candidate
                break

    additional = {}
    if "62" in fields:
        try:
            additional = _parse_tlv(fields["62"])
        except PixPayloadError:
            pass

    amount = None
    if fields.get("54"):
        try:
            amount = Decimal(fields["54"])
        except InvalidOperation:
            pass

    return PixPayload(
        merchant_name=fields.get("59", "").strip(),
        merchant_city=fields.get("60", "").strip(),
        amount=amount,
        key=merchant_account.get("01", "").strip(),
        txid=additional.get("05", "").strip(),
        crc_valid=crc_valid,
    )


def _parse_tlv(value: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    cursor = 0
    while cursor < len(value):
        if cursor + 4 > len(value):
            raise PixPayloadError("Campo incompleto no código Pix.")
        tag = value[cursor : cursor + 2]
        raw_length = value[cursor + 2 : cursor + 4]
        if not raw_length.isdigit():
            raise PixPayloadError("Tamanho de campo inválido no código Pix.")
        length = int(raw_length)
        start = cursor + 4
        end = start + length
        if end > len(value):
            raise PixPayloadError("Campo truncado no código Pix.")
        fields[tag] = value[start:end]
        cursor = end
    return fields


def _crc16_ccitt(data: bytes) -> str:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return f"{crc:04X}"
