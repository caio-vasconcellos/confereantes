import unittest

from confereantes.pix import PixPayloadError, _crc16_ccitt, parse_pix_payload


def build_pix_payload() -> str:
    merchant = "0014BR.GOV.BCB.PIX0114+5511999999999"
    additional = "0503***"
    merchant_name = "LOJA HORIZONTE"
    merchant_city = "JUNDIAI"
    prefix = (
        "000201"
        "010211"
        f"26{len(merchant):02d}{merchant}"
        "52040000"
        "5303986"
        "5406100.00"
        "5802BR"
        f"59{len(merchant_name):02d}{merchant_name}"
        f"60{len(merchant_city):02d}{merchant_city}"
        f"62{len(additional):02d}{additional}"
        "6304"
    )
    return prefix + _crc16_ccitt(prefix.encode("utf-8"))


class PixParserTests(unittest.TestCase):
    def test_rejects_duplicate_field_and_nonterminal_crc(self):
        for value in (build_pix_payload() + "5802BR", "0002010002016304ABCD"):
            with self.subTest(value=value), self.assertRaises(PixPayloadError):
                parse_pix_payload(value)

    def test_rejects_nonfinite_negative_or_malformed_amount(self):
        for amount in ("NaN", "Infinity", "-10.00", "0.00", "100.000"):
            value = build_pix_payload().replace("5406100.00", f"54{len(amount):02d}{amount}")
            with self.subTest(amount=amount), self.assertRaises(PixPayloadError):
                parse_pix_payload(value)

    def test_parses_valid_payload(self) -> None:
        payload = parse_pix_payload(build_pix_payload())

        self.assertTrue(payload.crc_valid)
        self.assertEqual(payload.merchant_name, "LOJA HORIZONTE")
        self.assertEqual(str(payload.amount), "100.00")
        self.assertEqual(payload.txid, "***")

    def test_rejects_truncated_payload(self) -> None:
        with self.assertRaises(PixPayloadError):
            parse_pix_payload("0002012636curto")


if __name__ == "__main__":
    unittest.main()
