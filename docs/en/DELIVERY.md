# Validation record — ConfereAntes

[English](DELIVERY.md) · [Português](../../ENTREGA.md)

Reviewed on 6 November 2026.

## Version 1.3 — English and Portuguese

- 58 Python tests and 18 subtests, 2 JavaScript tests and 1 C# integration test passed.
- English report and real local-model explanation checked in the browser with fictional data.
- Real Python → C# → Python flow, QR, history and local explanations passed in both languages.
- Language switch and 390 px layout checked, with no horizontal scrolling or console errors.
- [English report screenshot](../images/conferencia-en.png).

The following sections record the version 1.2 checks.

## Checks completed

| Area | Evidence |
| --- | --- |
| Images and text | Fictional offer image read through the browser; extracted text remained editable |
| QR code | Fictional QR image decoded into a reviewable field without opening its content |
| Rule engine | Synthetic scenarios for social engineering, amounts, recipients, domains and Pix |
| C# and Python | Real Python → C# → Python flow |
| EF Core history | Real SQLite, optional storage, encrypted payload, listing and clearing |
| Local model | Qwen 2.5 1.5B explanation inspected in the browser |
| Model failure | Rule score preserved and invalid output discarded |
| Interface protection | CSRF, escaped HTML, security headers and input limits; delayed-upload regression |
| Layout | Desktop result and 390 px mobile form reviewed, with no horizontal overflow or console errors |
| Repository | Public source, CI and screenshots containing fictional data only |

The 1.2 validation passed 50 Python tests with 18 subcases, two JavaScript tests and one C# integration test. The real-service smoke test also passed with the model enabled. The text acceptance set included 12 synthetic cases; this is not a representative fraud dataset or an accuracy measurement.

Screenshots: [desktop](../images/conferencia.png), [mobile](../images/celular.png). Both show the Portuguese 1.2 interface. See the [demo](DEMO.md) for reproduction steps.

## Known limits

The score represents warning rules, not a fraud probability. Educational wording, irony or missing context can trigger false findings; unknown patterns can be missed. OCR and approximate name matching can be wrong. CRC verifies integrity, not ownership or legitimacy.

The model may still be wrong after validation. It has no tools or authority to change the score. Initial model loading is slower. Installation requires internet; processing uses the local model after installation.

Python-only and full mode have separate histories. Local-profile keys do not protect against account compromise. No independent audit, regulatory assessment or statistical effectiveness study was performed.

The implemented scope is a local checking tool, not a banking certification service.
