# Demo walkthrough

[English](DEMO.md) · [Português](../../DEMONSTRACAO.md)

Use fictional data and do not make payments during the demo.

## Start

1. Run `scripts/start-ai.ps1` if you want local explanations. Install `qwen2.5:1.5b` once.
2. In another terminal, run `scripts/start-full.ps1`.
3. Open `http://127.0.0.1:8000/?lang=en`.

## Five-minute walkthrough

1. Click **Try an example**. The counter changes to 02/02 and payment details expand.
2. Point out the fictional amounts of R$ 1.850,00 and R$ 2.150,00 and the different recipient names.
3. Select the optional local explanation, then click **Check now**.
4. Inspect the score, findings and recommended checks. Explain that the score is not a fraud probability.
5. Compare the rule findings with the generated explanation. The model does not determine the score.
6. Start a new analysis with matching offer and request text: `Product for R$ 100,00. Collect in person.` A low result still asks the user to confirm the source.
7. Upload an offer screenshot or QR-code image. Review the extracted content without visiting links.
8. Save a fictional analysis and open **Local history** to demonstrate persistence.
9. Use **Print or save as PDF** to open the browser's print dialog.

Switch to **Português** to demonstrate localization. Evidence is not translated. English mode still handles Brazilian real amounts and Pix codes.

## Architecture to explain

Python handles images and rules. C# orchestrates analyses and stores results through EF Core. SQLite holds the encrypted payload. Ollama explains generic finding labels without receiving original evidence.

## Stop and repeat

Press Ctrl+C in the app and model terminals. Full mode stops the API it started.

To repeat the isolated end-to-end test, keep the app ports free and run `python scripts/smoke_completo.py --lang en --with-ai` with Ollama active. Omit `--with-ai` when no model is running.
