# Security and privacy

[Português](SEGURANCA-E-PRIVACIDADE.md) · [English](SECURITY-AND-PRIVACY.md)

ConfereAntes helps review information; it does not authorize payments or confirm the identity of a person or company. A low result does not prove that a request is legitimate. Pix CRC checks code integrity, not key ownership.

## Local data

- The app binds to `127.0.0.1` by default.
- Messages, images, written links and Pix codes are not sent to an external analysis service.
- Links are inspected as text and are never opened by the engine.
- Upload handling may use framework-managed temporary files. The app does not keep an image library.
- Installing dependencies and downloading the model require internet access; analysis uses the installed local components.

## History

History stays off until you select the save option. Content is encrypted before it is inserted into SQLite.

- Python mode: `%LOCALAPPDATA%\ConfereAntes\historico.sqlite3` and `historico.key`;
- C# mode: `%LOCALAPPDATA%\ConfereAntes\api\historico.db` with keys under `api\keys`.

The histories are independent. Deleting a key may make existing records unreadable. Because the keys stay in the same Windows profile, encryption does not protect against someone who already controls that account.

## Local explanation

When requested, the explanation sends Ollama only finding labels, generic recommendations, the level and the score. Original messages, names, links and Pix keys are not included. The response is not stored in history, cannot change the score and may be wrong.

## Interface safeguards

The project limits text, file, image and decoded QR-code sizes. Browser forms use CSRF protection; C# and Python communication uses a separate token. Responses include security headers, and displayed content is HTML-escaped. These controls reduce risk but are not a substitute for a security audit.

## Reporting a problem

Use fictional examples. Do not post personal screenshots, real Pix keys, passwords, tokens or verification codes in issues. Include the app, Python and browser versions and describe how to reproduce the problem.
