import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from confereantes.risk_engine import analyze


class RiskEngineTests(unittest.TestCase):
    def test_untrusted_urls_never_crash_analysis(self) -> None:
        for link in ("http://[", "https://[invalid]", "https://example.com:wrong", "https://example.com:99999", "file://localhost/test", "https://exemplo.com\nmalicioso"):
            with self.subTest(link=link):
                result = analyze(link=link)
                self.assertIn("Link malformado", [item.title for item in result.findings])

    def test_unseparated_thousands_compare_correctly(self) -> None:
        result = analyze(original_text="R$ 1850,00", received_text="R$ 850,00")
        self.assertIn("Valores divergentes", [item.title for item in result.findings])

    def test_equivalent_currency_formats_do_not_alert(self) -> None:
        result = analyze(original_text="R$ 1.850,00", received_text="R$ 1850,00")
        self.assertNotIn("Valores divergentes", [item.title for item in result.findings])

    def test_explicit_password_request_is_detected(self) -> None:
        result = analyze(received_text="Envie sua senha para liberar o produto.")
        self.assertIn("Pedido de senha ou código", [item.title for item in result.findings])

    def test_detects_urgent_payment_and_credential_request(self) -> None:
        result = analyze(
            received_text="Pague o Pix agora e envie o código de verificação. Sua conta será bloqueada.",
        )

        self.assertEqual(result.level, "alto")
        self.assertGreaterEqual(result.score, 55)
        self.assertGreaterEqual(
            {finding.title for finding in result.findings},
            {
                "Pressão ou urgência",
                "Pedido de senha ou código",
                "Pagamento combinado com urgência",
            },
        )

    def test_detects_changed_amount(self) -> None:
        result = analyze(
            original_text="Oferta anunciada por R$ 149,90.",
            received_text="Faça o Pix de R$ 499,90.",
        )

        self.assertEqual(result.level, "atencao")
        self.assertTrue(any(finding.title == "Valores divergentes" for finding in result.findings))

    def test_flags_shortened_non_https_link_without_opening_it(self) -> None:
        result = analyze(link="bit.ly/pagamento-seguro")

        self.assertEqual(result.level, "atencao")
        self.assertGreaterEqual(
            {finding.title for finding in result.findings},
            {"Link sem HTTPS", "Link encurtado"},
        )

    def test_neutral_text_has_low_score(self) -> None:
        result = analyze(
            original_text="Produto por R$ 100,00. Retirada presencial.",
            received_text="O valor permanece R$ 100,00. Confirme quando puder.",
        )

        self.assertEqual(result.level, "baixo")
        self.assertEqual(result.score, 0)
        self.assertEqual(result.findings, [])

    def test_detects_recipient_mismatch(self) -> None:
        result = analyze(
            expected_recipient="Loja Horizonte Ltda",
            displayed_recipient="Carlos da Silva",
        )

        self.assertEqual(result.level, "atencao")
        self.assertTrue(any(finding.title == "Destinatário divergente" for finding in result.findings))

    def test_accepts_small_variation_in_recipient_name(self) -> None:
        result = analyze(
            expected_recipient="José Comércio LTDA",
            displayed_recipient="Jose Comercio",
        )

        self.assertFalse(any(finding.title == "Destinatário divergente" for finding in result.findings))

    def test_flags_malformed_link(self) -> None:
        result = analyze(link="não é um endereço válido")

        self.assertTrue(any(finding.title == "Link malformado" for finding in result.findings))

    def test_flags_invalid_pix_integrity(self) -> None:
        result = analyze(pix="0002010102116304FFFF")

        self.assertTrue(
            any(
                finding.title in {"Código Pix foi alterado ou está corrompido", "Código Pix inválido ou incompleto"}
                for finding in result.findings
            )
        )


if __name__ == "__main__":
    unittest.main()
