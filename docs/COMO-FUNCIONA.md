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

Essa integração foi mantida porque mostra C# e EF Core em funcionamento real, mas deixou de ser apresentada como requisito ou como uma versão “mais completa” do aplicativo.

## Pastas principais

```text
src/confereantes/   interface, regras, Pix, OCR, QR, histórico e idiomas
api/                API C# e teste de integração
scripts/            configuração, inicialização e smoke test
tests/              testes Python e JavaScript
docs/               guias e imagens fictícias
```

## Decisões de escopo ainda abertas

- **Manter a API C#:** ela acrescenta valor de estudo, mas não é necessária para o uso comum. Retirá-la seria uma decisão de portfólio, não uma limpeza técnica automática.
- **Unificar os históricos:** Python e C# usam formatos e chaves diferentes. Uma unificação exige escolher um formato e criar uma migração para dados existentes.
- **Manter a explicação local:** ela é independente da pontuação e pode ser removida sem afetar as regras. Continua opcional para demonstrar integração local com um modelo.
- **Consultar bancos ou reputação de domínios:** isso exigiria serviços externos e mudaria a proposta de privacidade. O projeto atual não faz essas consultas.

Essas escolhas devem partir do objetivo do projeto. Nenhuma delas precisa ser decidida para usar ou demonstrar o fluxo principal.
