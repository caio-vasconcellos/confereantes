# Como o ConfereAntes funciona

[Português](COMO-FUNCIONA.md) · [English](HOW-IT-WORKS.md)

## Fluxo principal

```text
Navegador → FastAPI → regras de conferência
                    ↘ OCR e leitor de QR Code
                    ↘ histórico SQLite, quando solicitado
                    ↘ Ollama local, quando solicitado
```

O núcleo está em Python. A interface envia os dados para o FastAPI, que valida os campos e executa regras determinísticas. O resultado mostra cada alerta e a recomendação correspondente. Links são tratados como texto e códigos QR são apenas decodificados.

O modo padrão também pode extrair texto de imagens, guardar análises em SQLite com conteúdo criptografado e pedir uma explicação a um modelo local. OCR e IA podem errar, por isso o conteúdo continua editável e as regras permanecem visíveis.

## Integração C# opcional

`scripts/iniciar-completo.ps1` acrescenta uma API ASP.NET Core entre a interface e o processador Python:

```text
Navegador → FastAPI → API C# → regras Python
                         ↘ EF Core + SQLite
```

A API C# demonstra comunicação entre serviços, validação e persistência com EF Core. Ela não possui um segundo motor de risco. As chamadas usam endereços locais e um token criado pelo script de inicialização.

O modo Python funciona sozinho. Use a API C# se quiser executar a integração com EF Core.

## Pastas principais

```text
src/confereantes/   interface, regras, Pix, OCR, QR, histórico e idiomas
api/                API C# e teste de integração
scripts/            configuração, inicialização e smoke test
tests/              testes Python e JavaScript
docs/               guias e imagens fictícias
```

## Limites

Os históricos Python e C# usam formatos e chaves diferentes. Não há migração automática entre eles.

O aplicativo não consulta bancos nem serviços de reputação de domínios. A IA local apenas resume os alertas; não decide a pontuação nem confirma se um pagamento é seguro.
