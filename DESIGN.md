# Mesa de checagem

[English](docs/en/DESIGN.md) · [Português](DESIGN.md)

A interface parte de uma mesa com dois documentos: o combinado (A) e a cobrança (B). O símbolo [≠] representa o trabalho de comparar, não uma conclusão sobre a cobrança.

O painel laranja acompanha o formulário e mostra quantas evidências foram inseridas. O restante da superfície fica reservado à leitura e ao resultado. Os dados de pagamento são complementares e ficam em uma seção expansível.

## Referências pesquisadas

- [Hoverstat.es — arquivo experimental](https://www.hoverstat.es/archive/?tagged=experimental): composições alternativas, navegação e interfaces que apresentam personalidade pela estrutura.
- [Treize Grammes](https://www.13g.fr/): identidade tipográfica e direção de marca.
- [Are.na](https://www.are.na/): organização de materiais em uma ferramenta de pesquisa.

A aplicação tem desenho próprio; não utiliza código, imagens ou fontes proprietárias desses sites.

## Decisões

- Laranja de sinalização, cinza de bancada e preto; cores dos alertas continuam acompanhadas por texto.
- Tipografia condensada nos títulos e monoespaçada nas referências de documento.
- Formulários A/B, folha pautada e numeração dos achados.
- Sem fontes externas ou imagens baixadas: a interface funciona localmente.
- Navegação por teclado, atalho para o formulário e redução de movimento respeitada.
- Em telas pequenas, os documentos e o painel passam para uma única coluna.

O estilo está em `src/confereantes/static/workbench.css`.
