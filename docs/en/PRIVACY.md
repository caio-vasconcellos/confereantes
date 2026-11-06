# Privacy

[English](PRIVACY.md) · [Português](../../PRIVACIDADE.md)

ConfereAntes processes messages, screenshots, written links, Pix codes and recipient names on the local computer.

## Images and text

Uploaded files may use temporary storage managed by the web framework. OCR reads their bytes in memory. The app does not keep an image library or send evidence to an external analysis API.

Changing the interface language does not translate the evidence. Text stays as entered, including accents, names and Brazilian currency formatting.

## Optional history

History is off by default. When selected, the app saves a result and short evidence excerpts, encrypted before insertion into SQLite.

Python-only mode stores `historico.sqlite3` and `historico.key` under `%LOCALAPPDATA%/ConfereAntes`. Full mode keeps a separate database at `api/historico.db` and Data Protection keys under `api/keys`. No automatic migration takes place between modes. The history page displays the database for the active mode.

Deleting a key can make existing records unreadable. Keys remain in the same local profile; encryption does not protect against someone who already controls that account. History can be cleared from the interface.

## Optional explanation

Ollama receives finding labels, generic recommendations, level and score. Original messages, names, links and Pix keys are not included. Explanations are not stored in history. The selected language is sent to the local processor so it can request the appropriate output language.

Installing dependencies and downloading models requires internet. Inference uses `127.0.0.1:11434`. Use `scripts/start-ai.ps1` to disable Ollama cloud features.

## Network

The services bind to loopback by default. Links supplied as evidence are inspected as text and are never visited. Do not add real evidence, databases or keys to Git.
