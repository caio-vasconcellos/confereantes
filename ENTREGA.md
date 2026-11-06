# Registro de validação — ConfereAntes

[English](docs/en/DELIVERY.md) · [Português](ENTREGA.md)

Data: 6 de novembro de 2026.

## Versão 1.3 — português e inglês

- 58 testes Python e 18 subcasos, 2 testes JavaScript e 1 integração C# aprovados.
- Relatório e explicação local em inglês conferidos no navegador, com dados fictícios.
- Fluxo real Python → C# → Python, QR, histórico e IA local aprovado nos dois idiomas.
- Seletor de idioma e layout em 390 px conferidos, sem rolagem horizontal ou erros de console.
- [Captura do relatório em inglês](docs/images/conferencia-en.png).

Os resultados abaixo registram a validação da versão 1.2.

## Estado

Este registro reúne os testes da versão 1.2: comparação de evidências de cobrança, OCR, QR Code, API C#, EF Core/SQLite e explicação opcional por IA local. As mudanças posteriores estão no [histórico de versões](CHANGELOG.md).

## Critérios de aceitação

| Critério | Resultado e evidência |
| --- | --- |
| Texto e imagem | OCR de imagem fictícia conferido na interface; texto extraído revisável |
| QR Code | Imagem fictícia lida na interface; endereço preenchido sem navegação |
| Regras e comparação | Cenários fictícios de engenharia social, valores, destinatários, domínios e Pix cobertos por testes |
| C# / Python | Fluxo real Python → C# → Python aprovado |
| EF Core e histórico | SQLite real, gravação opcional, conteúdo protegido, consulta e limpeza aprovados |
| IA generativa local | Qwen 2.5 1.5B executado neste computador; explicação estruturada conferida no navegador |
| Falha de IA | Não altera a pontuação; saída inválida descartada e regras continuam disponíveis |
| Privacidade | Evidências não são enviadas a API externa; modelos e dados locais fora do Git |
| Proteção da interface | CSRF, escape de HTML, cabeçalhos e limites verificados; regressão de upload assíncrono coberta |
| Desktop e celular | Resultado desktop e formulário em viewport de 390 px conferidos; sem overflow horizontal; console sem erros |
| Demonstração e instalação | Scripts Windows, arquitetura, privacidade, segurança e roteiro de demonstração documentados |
| Repositório | Código público, integração contínua Python/JavaScript/C# e capturas somente com dados fictícios |

## Testes executados

- 50 testes Python aprovados, incluindo 18 subcasos.
- 2 testes JavaScript aprovados para preservar edições durante uploads.
- 1 teste de integração C# aprovado: autenticação, validação e histórico protegido.
- `scripts/smoke_completo.py --with-ai` aprovado com serviços e modelo reais, banco isolado e evidências fictícias.
- Cenários de texto incluem 12 casos sintéticos de aceitação além das regressões unitárias. Esses casos não constituem uma amostra de golpes reais nem medem taxa de acerto.

As capturas estão em [desktop](docs/images/conferencia.png) e [celular](docs/images/celular.png). O roteiro reproduzível está em [DEMONSTRACAO.md](DEMONSTRACAO.md).

## Limites conhecidos, aceitos no escopo

- A pontuação representa regras de atenção, não probabilidade de fraude. Frases educativas, ironia ou contexto ausente podem produzir falsos alertas; golpes sem os sinais conhecidos podem passar despercebidos.
- OCR e comparação aproximada de nomes podem errar. O usuário revisa o conteúdo antes da análise.
- CRC confirma integridade do código Pix, não titularidade, existência da chave ou legitimidade do destinatário. Não há consulta bancária.
- A IA pode errar mesmo quando a resposta passa pelas verificações. Não decide risco, não recebe evidências originais e não executa ações.
- O primeiro carregamento dos modelos é mais lento. A instalação exige internet; o uso com os modelos instalados é local.
- Os modos Python e completo mantêm históricos separados. Não há migração automática entre eles.
- As chaves no mesmo perfil local não protegem contra alguém que já controla a conta do computador.
- Não foi realizada auditoria externa, certificação de acessibilidade ou estudo estatístico de eficácia. A entrega não pretende certificar adequação a uso bancário em produção.

Esses limites definem o produto entregue e estão expostos na documentação; não são funcionalidades prometidas e ausentes.
