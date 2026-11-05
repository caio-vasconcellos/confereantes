"""Teste real dos serviços locais com dados fictícios e banco isolado.

Execute depois de compilar a API. Acrescente --with-ai com Ollama/modelo ativos.
"""
import argparse
import io
import os
from pathlib import Path
import secrets
import shutil
import sqlite3
import subprocess
import sys
import time
from uuid import uuid4

import httpx
import qrcode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-ai", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    portable = root / ".tools" / "dotnet" / ("dotnet.exe" if os.name == "nt" else "dotnet")
    dotnet = str(portable) if portable.exists() else shutil.which("dotnet")
    if not dotnet:
        raise RuntimeError("Instale o SDK .NET 10.")
    database_dir = root / ".test-data" / uuid4().hex
    env = {**os.environ, "CONFEREANTES_SERVICE_TOKEN": secrets.token_hex(32), "CONFEREANTES_USE_API": "1", "CONFEREANTES_API_DATA_DIR": str(database_dir)}
    processes = []
    try:
        for command in (
            [dotnet, str(root / "api/ConfereAntes.Api/bin/Debug/net10.0/ConfereAntes.Api.dll")],
            [sys.executable, "-m", "uvicorn", "confereantes.main:app", "--host", "127.0.0.1", "--port", "8000"],
        ):
            processes.append(subprocess.Popen(command, cwd=root, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        with httpx.Client(trust_env=False, timeout=220) as client:
            for port in (5080, 8000):
                for _ in range(100):
                    if any(process.poll() is not None for process in processes):
                        raise RuntimeError("Um serviço encerrou durante a inicialização. Verifique se as portas estão livres.")
                    try:
                        if client.get(f"http://127.0.0.1:{port}/saude").status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(.2)
                else:
                    raise RuntimeError(f"Serviço {port} não iniciou.")
            print("Serviços locais iniciados.", flush=True)
            headers = {"X-ConfereAntes-Token": env["CONFEREANTES_SERVICE_TOKEN"]}
            api = "http://127.0.0.1:5080"
            ui = "http://127.0.0.1:8000"
            assert client.get(api + "/historico").status_code == 401
            assert client.post(ui + "/api/analisar", json={"received_text": "Pix agora"}).status_code == 401
            image = qrcode.make("https://exemplo.invalid/cobranca")
            output = io.BytesIO()
            image.save(output, "PNG")
            response = client.post(ui + "/api/qr", files={"image": ("teste.png", output.getvalue(), "image/png")})
            assert response.status_code == 200, response.text
            assert response.json()["text"] == "https://exemplo.invalid/cobranca"
            payload = {"original_text": "Produto de R$ 100,00", "received_text": "Faça Pix de R$ 200,00 agora e envie a senha."}
            direct = client.post(api + "/analises", json=payload, headers=headers)
            assert direct.status_code == 200, direct.text
            assert direct.json()["level"] == "alto"
            print("QR e análise C# -> Python aprovados.", flush=True)
            assert client.get(api + "/historico", headers=headers).json() == []
            response = client.post(ui + "/analisar", data={**payload, "save_history": "1", "use_ai": "1" if args.with_ai else ""})
            assert response.status_code == 200, response.text
            assert "Nível: Alto" in response.text
            if args.with_ai:
                assert "Explicação gerada localmente" in response.text
                assert "IA local indisponível" not in response.text
            history = client.get(api + "/historico", headers=headers).json()
            assert len(history) == 1
            assert history[0]["received_excerpt"] == payload["received_text"]
            assert client.get(ui + "/historico").status_code == 200
            with sqlite3.connect(database_dir / "historico.db") as connection:
                encrypted = connection.execute("SELECT ProtectedPayload FROM Analyses").fetchone()[0]
            assert payload["received_text"] not in encrypted
            assert client.post(ui + "/historico/limpar").status_code == 303
            assert client.get(api + "/historico", headers=headers).json() == []
        print("OK: QR real, token, Python -> C# -> Python, EF Core/SQLite criptografado, leitura e limpeza do histórico" + (", IA local real" if args.with_ai else ""))
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)


if __name__ == "__main__":
    main()
