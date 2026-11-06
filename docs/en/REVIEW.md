# Review notes

[English](REVIEW.md) · [Português](../../REVISAO.md)

The initial review compared the implementation with the original learning plan. Version 1.1 added its missing functional parts: QR decoding, the C# API, EF Core and local model explanations. Version 1.2 covered the remaining browser checks and regressions. Version 1.3 adds English and revises the documentation.

| Requirement | Implementation |
| --- | --- |
| Compare two screenshots or messages | A/B form, local OCR and editable text |
| Compare amounts and recipients | Deterministic rules; approximate name matching |
| Inspect a domain without opening it | Text inspection, with no reputation lookup |
| Read Pix content | TLV parsing, CRC validation and QR decoding |
| Explain social-engineering signals | Urgency, secrecy, credential and remote-access rules |
| Local generative explanation | Optional Ollama client; independent of the score |
| C# API with Python processing | Authenticated loopback calls in full mode |
| EF Core and SQLite | Opt-in encrypted history |
| Documentation and tests | README, setup scripts, tests and CI |
| English and Portuguese | UI, reports, history, errors, documentation and local explanations |

Pix validation remains limited to the supported structure and checksum. The app does not query key ownership or certify the recipient.

## Publication checks

Tracked files and historical file names were reviewed for personal screenshots, analysis databases and virtual environments. A search for common token and private-key patterns found no matches. This was a limited review, not an independent audit.

Examples are fictional. Models and runtime files are ignored by Git. Commit author email addresses are part of the public Git history. The project has no reuse license selected by the author; repository visibility is not itself a software license.

## Validation boundaries

The project has automated tests and local browser checks, but no external penetration test, accessibility certification or statistical study of fraud-detection accuracy. Public GitHub visibility exposes the source and history; the app still runs locally.

See the [validation record](DELIVERY.md) for the completed 1.2 checks and the [changelog](CHANGELOG.md) for later work.
