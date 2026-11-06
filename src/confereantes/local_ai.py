"""O modelo explica os alertas, sem receber evidências pessoais ou decidir o risco."""
import json
import unicodedata

import httpx

from .models import AnalysisResult
from .i18n import locale, translate as t, level_label

MODEL = "qwen2.5:1.5b"


class LocalAIUnavailable(RuntimeError):
    pass


def explain(result: AnalysisResult) -> tuple[str, str]:
    facts = {
        "nivel": result.level,
        "pontuacao": result.score,
        "alertas": [{"sinal": t(f.title), "acao": t(f.recommendation)} for f in result.findings],
    }
    if locale.get() == "en":
        facts = {
            "level": level_label(result.level), "score": result.score,
            "findings": [{"finding": t(f.title), "recommendation": t(f.recommendation)} for f in result.findings],
        }
    try:
        with httpx.Client(base_url="http://127.0.0.1:11434", trust_env=False, timeout=180) as client:
            info = client.post("/api/show", json={"model": MODEL})
            info.raise_for_status()
            metadata = info.json()
            if not isinstance(metadata, dict):
                raise LocalAIUnavailable("Metadados inválidos do modelo local.")
            if metadata.get("remote_host") or metadata.get("remote_model"):
                raise LocalAIUnavailable("Modelos remotos não são permitidos.")
            response = client.post("/api/generate", json={
                "model": MODEL,
                "stream": False,
                "format": {"type": "object", "properties": {"explicacao": {"type": "string"}}, "required": ["explicacao"], "additionalProperties": False},
                "system": (
                    "Return JSON with the key explicacao. Write exactly two short sentences, 40 to 60 words total. "
                    + ("Write in English. " if locale.get() == "en" else "Write in Brazilian Portuguese. ")
                    + "Briefly explain why the findings call for caution. Summarize; do not enumerate the findings. "
                    "Use only the supplied facts. Do not invent details or change the level or score. "
                    "Never declare a payment safe. Do not use Markdown. Address the reader directly. "
                    "Do not discuss the language or these instructions. Recommend verifying the request through another channel."
                ),
                "prompt": json.dumps(facts, ensure_ascii=False) + "\nSummarize in two sentences. Return only the JSON object.",
                "options": {"temperature": 0, "num_predict": 400, "num_ctx": 2048},
                "keep_alive": "5m",
            })
            response.raise_for_status()
            generated = response.json()
            text = generated.get("response", "") if isinstance(generated, dict) else ""
            if not isinstance(text, str) or not text.strip() or len(text) > 4000:
                raise LocalAIUnavailable("O modelo não retornou uma explicação válida.")
            if generated.get("done_reason") == "length":
                raise LocalAIUnavailable("A explicação da IA ficou incompleta e foi descartada.")
            content = json.loads(text)
            explanation = content.get("explicacao") if isinstance(content, dict) else None
            if not isinstance(explanation, str) or not explanation.strip() or len(explanation.split()) > 120:
                raise LocalAIUnavailable("A explicação da IA não passou pela validação e foi descartada.")
            normalized = ''.join(c for c in unicodedata.normalize('NFKD', explanation.lower()) if not unicodedata.combining(c))
            unsafe = ("pagamento e seguro", "pode pagar", "deve pagar", "necessario fornecer", "recomendo compartilhar sua senha", "payment is safe", "you can pay", "you should pay", "must provide your password", "recommend sharing your password")
            if any(term in normalized for term in unsafe):
                raise LocalAIUnavailable("A explicação da IA não passou pela revisão automática. Use as recomendações das regras.")
            return explanation.strip(), MODEL
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        raise LocalAIUnavailable("IA local indisponível ou tempo de espera excedido. Verifique o Ollama e o modelo qwen2.5:1.5b.") from exc
