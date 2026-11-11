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

This integration remains useful as a working C# and EF Core example, but it is no longer presented as a requirement or as a “more complete” edition of the app.

## Main directories

```text
src/confereantes/   interface, rules, Pix, OCR, QR, history and languages
api/                C# API and integration test
scripts/            setup, launchers and smoke test
tests/              Python and JavaScript tests
docs/               guides and fictional screenshots
```

## Open scope choices

- **Keep the C# API:** it adds learning value but is not needed for ordinary use. Removing it is a portfolio decision, not automatic cleanup.
- **Merge the histories:** Python and C# use different formats and keys. Merging them requires a chosen format and a migration for existing data.
- **Keep local explanations:** they are independent of the score and can be removed without changing the rules. They remain optional to demonstrate local-model integration.
- **Query banks or domain-reputation services:** this would require external services and change the privacy model. The current project makes no such requests.

These choices should follow the project's goal. None is required to use or demonstrate the main flow.
