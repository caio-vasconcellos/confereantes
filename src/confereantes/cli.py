from __future__ import annotations

import argparse
import os
import threading
import webbrowser

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ConfereAntes on your computer.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--lang", choices=("pt", "en"), default=os.environ.get("CONFEREANTES_LANG"), help="Browser interface language")
    args = parser.parse_args()

    if not args.no_browser:
        url = f"http://{args.host}:{args.port}"
        if args.lang:
            url += f"?lang={args.lang}"
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    uvicorn.run("confereantes.main:app", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
