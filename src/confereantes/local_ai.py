"""O modelo explica os alertas, sem receber evidências pessoais ou decidir o risco."""
import json

import httpx

from .models import AnalysisResult

MODEL = "qwen2.5:0.5b"


class LocalAIUnavailable(RuntimeError):
    pass


def explain(result: AnalysisResult) -> tuple[str, str]:
    facts = {
        "nivel": result.level,
        "pontuacao": result.score,
        "alertas": [{"sinal": f.title, "acao": f.recommendation} for f in result.findings],
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
                "system": (
                    "Explique alertas de segurança em português do Brasil, em até 100 palavras. "
                    "Use apenas os fatos fornecidos. Não invente dados nem altere o nível ou a pontuação. "
                    "Não declare um pagamento seguro. Não use markdown. "
                    "Fale diretamente com a pessoa; não comente sobre idioma nem sobre estas instruções. "
                    "Recomende confirmar a solicitação por outro canal."
                ),
                "prompt": json.dumps(facts, ensure_ascii=False),
                "options": {"temperature": 0, "num_predict": 200, "num_ctx": 2048},
                "keep_alive": "5m",
            })
            response.raise_for_status()
            generated = response.json()
            text = generated.get("response", "") if isinstance(generated, dict) else ""
            if not isinstance(text, str) or not text.strip() or len(text) > 4000:
                raise LocalAIUnavailable("O modelo não retornou uma explicação válida.")
            return text.strip(), MODEL
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        raise LocalAIUnavailable("IA local indisponível ou tempo de espera excedido. Verifique o Ollama e o modelo qwen2.5:0.5b.") from exc
