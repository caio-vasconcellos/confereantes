# Histórico de versões

[English](docs/en/CHANGELOG.md) · [Português](CHANGELOG.md)

## 1.3.0 — 2026-11-06

- interface em português e inglês, com seletor de idioma;
- relatórios, histórico, mensagens de erro e explicações locais em inglês;
- detecção de termos de engenharia social em inglês;
- README, documentação e comandos de instalação em inglês;
- revisão de redação, com descrições diretas das funções e dos limites.

## 1.2.0 — 2026-11-06

- entrega final do escopo local de portfólio, com relatório de aceitação e demonstração;
- validação visual do fluxo completo e do formulário móvel, com capturas fictícias;
- modelo local Qwen 2.5 1.5B e explicações JSON validadas; descarte de saída truncada;
- proteção CSRF em formulários e uploads, compatível com navegador integrado;
- OCR e QR preservam campos editados durante uma leitura assíncrona;
- links malformados não interrompem a análise;
- comparação correta de valores como `1850,00` e `1.850,00`;
- rejeição de Pix com campos repetidos, CRC fora do fim ou valor inválido;
- ampliação para 50 testes Python, 2 testes JavaScript e integração C#.

## 1.1.0 — 2026-11-04

- leitura local de QR Code com preenchimento revisável do Pix ou link;
- API ASP.NET Core em C# para orquestração e histórico;
- persistência EF Core/SQLite com payload protegido por ASP.NET Data Protection;
- comunicação interna autenticada por token efêmero;
- explicação opcional com Ollama, sem alterar pontuação ou receber evidências originais;
- modo completo e modo Python independente, com históricos separados;
- testes do leitor QR, isolamento da IA e API C#.

## 1.0.0 — 2026-11-04

- fluxo completo de análise de textos, imagens, links e Pix;
- OCR local com revisão manual;
- comparação de valores e destinatários;
- validação estrutural e CRC do Pix copia e cola;
- histórico local criptografado e opcional;
- impressão do relatório;
- cabeçalhos, limites e validações de segurança;
- inicialização simplificada no Windows;
- suíte de testes e integração contínua.

## 0.1.0 — 2026-10-30

- primeiro motor local de regras;
- interface inicial e quatro testes unitários.
