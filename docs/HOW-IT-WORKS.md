# How ConfereAntes works

[Português](COMO-FUNCIONA.md) · [English](HOW-IT-WORKS.md)

## Main flow

```text
Browser → FastAPI → review rules
                  ↘ OCR and QR-code reader
                  ↘ SQLite history, when requested
                  ↘ local Ollama model, when requested
```

The core is written in Python. The interface sends data to FastAPI, which validates the fields and runs deterministic rules. The report shows every finding and its recommendation. Links are handled as text, and QR codes are only decoded.

The default mode can also extract text from images, store analyses in SQLite with encrypted content and ask a local model for an explanation. OCR and model output may be wrong, so extracted content stays editable and the rule findings remain visible.

## Optional C# integration

`scripts/start-full.ps1` adds an ASP.NET Core API between the interface and the Python processor:

```text
Browser → FastAPI → C# API → Python rules
                       ↘ EF Core + SQLite
```

The C# API demonstrates service communication, validation and EF Core persistence. It does not contain a second risk engine. Requests use loopback addresses and a token created by the launcher.

The Python mode works on its own. Use the C# API to run the EF Core integration.

## Main directories

```text
src/confereantes/   interface, rules, Pix, OCR, QR, history and languages
api/                C# API and integration test
scripts/            setup, launchers and smoke test
tests/              Python and JavaScript tests
docs/               guides and fictional screenshots
```

## Limits

The Python and C# histories use different formats and keys. There is no automatic migration between them.

The app does not query banks or domain-reputation services. The local model only summarizes findings; it does not set the score or confirm that a payment is safe.
