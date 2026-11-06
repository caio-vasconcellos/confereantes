"""Cenários fictícios de aceitação; não medem precisão em golpes reais."""
import pytest

from confereantes.risk_engine import analyze


@pytest.mark.parametrize("evidence, expected", [
    ({"received_text": "Mantenha em segredo e apague a conversa."}, "Pedido de sigilo"),
    ({"received_text": "Instale AnyDesk para receber o estorno."}, "Solicitação de acesso remoto"),
    ({"received_text": "Compartilhe sua tela no TeamViewer."}, "Solicitação de acesso remoto"),
    ({"received_text": "Informe sua senha para confirmar a compra."}, "Pedido de senha ou código"),
    ({"received_text": "Envie o código de verificação."}, "Pedido de senha ou código"),
    ({"received_text": "Faça a transferência imediatamente."}, "Pagamento combinado com urgência"),
    ({"link": "https://loja.exemplo@outro.invalid/pagar"}, "Link tenta esconder o domínio real"),
    ({"link": "https://192.0.2.1/pagar"}, "Link usa endereço IP"),
    ({"link": "https://xn--exemplo-9za.invalid"}, "Domínio internacionalizado"),
    ({"link": "https://tinyurl.com/teste"}, "Link encurtado"),
    ({"original_text": "R$ 2500,00", "received_text": "R$ 500,00"}, "Valores divergentes"),
    ({"expected_recipient": "Loja fictícia A", "displayed_recipient": "Destinatário B"}, "Destinatário divergente"),
])
def test_synthetic_acceptance_scenarios(evidence, expected):
    result = analyze(**evidence)
    assert expected in {finding.title for finding in result.findings}
    assert 0 <= result.score <= 100
    assert all(finding.recommendation for finding in result.findings)
