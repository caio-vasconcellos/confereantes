"""Cliente interno da API C#, restrito ao loopback e sem proxy externo."""
import os

import httpx


def api_enabled() -> bool:
    return os.environ.get("CONFEREANTES_USE_API") == "1"


def service_token() -> str:
    return os.environ.get("CONFEREANTES_SERVICE_TOKEN", "")


async def api_request(method: str, path: str, payload=None):
    token = service_token()
    if not token:
        raise RuntimeError("Token interno ausente. Use scripts/iniciar-completo.ps1.")
    async with httpx.AsyncClient(base_url="http://127.0.0.1:5080", trust_env=False, timeout=210) as client:
        response = await client.request(method, path, json=payload, headers={"X-ConfereAntes-Token": token})
        response.raise_for_status()
        return response.json() if response.content else None
