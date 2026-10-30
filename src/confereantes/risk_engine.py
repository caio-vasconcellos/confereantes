from __future__ import annotations

import ipaddress
import re
from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

from .models import AnalysisResult, Finding


URGENCY_TERMS = (
    "agora",
    "imediatamente",
    "última chance",
    "ultima chance",
    "prazo termina",
    "conta bloqueada",
    "será bloqueada",
    "sera bloqueada",
    "só hoje",
    "so hoje",
)
SECRECY_TERMS = (
    "não conte",
    "nao conte",
    "mantenha em segredo",
    "não avise",
    "nao avise",
    "apague a conversa",
)
CREDENTIAL_TERMS = (
    "envie o código",
    "envie o codigo",
    "código de verificação",
    "codigo de verificacao",
    "informe sua senha",
    "compartilhe sua senha",
    "token de acesso",
)
REMOTE_ACCESS_TERMS = (
    "anydesk",
    "teamviewer",
    "acesso remoto",
    "instale este aplicativo",
    "compartilhe sua tela",
)
PAYMENT_TERMS = (
    "pix",
    "transferência",
    "transferencia",
    "pague",
    "pagamento",
    "depósito",
    "deposito",
)
SHORTENERS = {
    "bit.ly",
    "cutt.ly",
    "is.gd",
    "rebrand.ly",
    "shorturl.at",
    "t.co",
    "tinyurl.com",
}


def analyze(
    *,
    original_text: str = "",
    received_text: str = "",
    link: str = "",
    pix: str = "",
) -> AnalysisResult:
    """Analisa evidências usando regras locais, explicáveis e determinísticas."""

    findings: list[Finding] = []
    combined = _normalize(" ".join((original_text, received_text)))

    _add_term_finding(
        findings,
        combined,
        URGENCY_TERMS,
        title="Pressão ou urgência",
        evidence="A mensagem usa linguagem que tenta acelerar a decisão.",
        recommendation="Pare e confirme a solicitação por um canal oficial antes de agir.",
        points=20,
    )
    _add_term_finding(
        findings,
        combined,
        SECRECY_TERMS,
        title="Pedido de sigilo",
        evidence="A mensagem tenta impedir que você consulte outra pessoa.",
        recommendation="Converse com alguém de confiança e confirme a identidade do remetente.",
        points=25,
    )
    _add_term_finding(
        findings,
        combined,
        CREDENTIAL_TERMS,
        title="Pedido de senha ou código",
        evidence="Foi encontrado um pedido relacionado a senha, token ou código de verificação.",
        recommendation="Não compartilhe códigos, senhas ou tokens. Acesse o serviço pelo aplicativo oficial.",
        points=40,
    )
    _add_term_finding(
        findings,
        combined,
        REMOTE_ACCESS_TERMS,
        title="Solicitação de acesso remoto",
        evidence="A conversa menciona ferramenta ou procedimento de acesso remoto.",
        recommendation="Não instale nem autorize acesso remoto solicitado por mensagem ou ligação inesperada.",
        points=45,
    )

    if _contains_any(combined, PAYMENT_TERMS) and _contains_any(combined, URGENCY_TERMS):
        findings.append(
            Finding(
                severity="alto",
                title="Pagamento combinado com urgência",
                evidence="A solicitação de pagamento aparece junto de pressão para agir rapidamente.",
                recommendation="Não pague. Confirme valor, destinatário e motivo diretamente com a parte envolvida.",
                points=25,
            )
        )

    findings.extend(_inspect_link(link))
    findings.extend(_compare_amounts(original_text, received_text))

    if pix.strip() and not pix.strip().startswith("000201"):
        findings.append(
            Finding(
                severity="atencao",
                title="Identificador Pix precisa de confirmação",
                evidence="O conteúdo informado não tem o prefixo comum de um código Pix copia e cola.",
                recommendation="Confirme no aplicativo do banco o nome e o CPF/CNPJ exibidos antes de autorizar.",
                points=15,
            )
        )

    score = min(100, sum(item.points for item in findings))
    level = "alto" if score >= 55 else "atencao" if score >= 25 else "baixo"
    return AnalysisResult(score=score, level=level, findings=findings)


def _add_term_finding(
    findings: list[Finding],
    text: str,
    terms: Iterable[str],
    *,
    title: str,
    evidence: str,
    recommendation: str,
    points: int,
) -> None:
    if _contains_any(text, terms):
        findings.append(
            Finding(
                severity="alto" if points >= 35 else "atencao",
                title=title,
                evidence=evidence,
                recommendation=recommendation,
                points=points,
            )
        )


def _inspect_link(raw_link: str) -> list[Finding]:
    value = raw_link.strip()
    if not value:
        return []

    parsed = urlparse(value if "://" in value else f"http://{value}")
    host = (parsed.hostname or "").lower().rstrip(".")
    findings: list[Finding] = []

    if parsed.scheme != "https":
        findings.append(
            Finding(
                severity="atencao",
                title="Link sem HTTPS",
                evidence="O endereço não usa uma conexão HTTPS explícita.",
                recommendation="Não abra o link. Digite manualmente o endereço oficial no navegador.",
                points=15,
            )
        )

    if host in SHORTENERS:
        findings.append(
            Finding(
                severity="atencao",
                title="Link encurtado",
                evidence=f"O domínio {host} esconde o destino final do endereço.",
                recommendation="Confirme o endereço completo pelo canal oficial antes de acessar.",
                points=25,
            )
        )

    if "xn--" in host:
        findings.append(
            Finding(
                severity="alto",
                title="Domínio internacionalizado",
                evidence="O domínio usa codificação que pode imitar caracteres de outro endereço.",
                recommendation="Não abra o link; procure o site oficial manualmente.",
                points=35,
            )
        )

    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        findings.append(
            Finding(
                severity="alto",
                title="Link usa endereço IP",
                evidence="O endereço aponta diretamente para um IP em vez de um domínio reconhecível.",
                recommendation="Não abra o link e confirme o endereço oficial da organização.",
                points=35,
            )
        )

    return findings


def _compare_amounts(original_text: str, received_text: str) -> list[Finding]:
    original = _extract_brl_amounts(original_text)
    received = _extract_brl_amounts(received_text)
    if not original or not received or original == received:
        return []
    return [
        Finding(
            severity="alto",
            title="Valores divergentes",
            evidence=f"Valores no anúncio: {_format_amounts(original)}; na cobrança: {_format_amounts(received)}.",
            recommendation="Não pague até que a divergência seja explicada e confirmada por um canal oficial.",
            points=40,
        )
    ]


def _extract_brl_amounts(text: str) -> set[Decimal]:
    amounts: set[Decimal] = set()
    for match in re.findall(r"(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{2}))", text, flags=re.IGNORECASE):
        normalized = match.replace(".", "").replace(",", ".")
        try:
            amounts.add(Decimal(normalized))
        except InvalidOperation:
            continue
    return amounts


def _format_amounts(amounts: set[Decimal]) -> str:
    return ", ".join(f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for amount in sorted(amounts))


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())

