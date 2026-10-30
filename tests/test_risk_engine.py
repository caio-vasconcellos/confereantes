import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from confereantes.risk_engine import analyze


class RiskEngineTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
