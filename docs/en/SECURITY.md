# Security

[English](SECURITY.md) · [Português](../../SEGURANCA.md)

## Reporting a problem

Use fictional examples in issues. Do not include personal screenshots, real Pix keys, passwords, tokens or verification codes. Include the app, Python and browser versions and steps to reproduce the problem.

## Controls

- Loopback addresses by default; accepted Python hosts restricted to localhost, 127.0.0.1 and the test host.
- Ephemeral service token between C# and Python; a separate CSRF token for browser forms and uploads.
- Security headers, content policy, escaped HTML and no-store responses.
- Limits on text length, image type, upload size, pixel count and decoded QR content.
- Written links are never opened; multiple QR codes are rejected.
- History is opt-in and its content is encrypted before storage.
- Interactive API documentation is disabled in the local app.
- Internal HTTP clients do not use external proxies or follow redirects.
- The local model receives rule labels and generic recommendations, not original evidence.
- Model output cannot change the score. Invalid or truncated responses and some known unsafe phrases are rejected.

The model checks do not guarantee semantic correctness. Neither the rules nor the model certify a payment. Confirm requests with the bank, company, platform or person involved.

No independent penetration test, security certification or regulatory assessment has been performed.
