# Revisão do projeto

Revisão em 4 de novembro de 2026, comparando a implementação com a proposta do ConfereAntes e o roteiro de aprendizagem de 12 semanas.

## Atendimento ao roteiro

| Critério | Situação | Evidência |
| --- | --- | --- |
| Ferramenta útil, demonstrável e diferente de um chatbot | Atendido no MVP | Interface de comparação A/B e exemplo fictício |
| Receber duas imagens e texto | Atendido | Formulário, rota de upload e OCR local |
| Comparar valores e destinatários | Atendido, com limitações | Regras determinísticas; nomes comparados aproximadamente |
| Analisar domínio sem abrir links suspeitos | Atendido no MVP | Inspeção textual; sem consulta de reputação |
| Pix copia e cola | Parcial | Parser TLV e CRC; não verifica titularidade ou validade junto ao banco |
| Ler QR Code de uma imagem | Implementado na 1.1 | Decoder ZXing, preenchimento revisável e limites de upload |
| Identificar sinais de engenharia social | Atendido no MVP | Regras de urgência, sigilo, credenciais e acesso remoto |
| Relatório explicativo | Atendido com regras | Evidências, recomendações e impressão pelo navegador |
| IA generativa local para explicações | Implementado como opção na 1.1 | Cliente Ollama para modelo local; não altera a pontuação e não recebe evidências originais |
| API em C# e processamento em Python | Implementado no modo completo | API ASP.NET Core orquestra chamadas ao processador Python autenticado |
| SQLite e histórico local | Atendido no MVP | Salvamento opcional com conteúdo criptografado |
| EF Core | Implementado na 1.1 | API salva e consulta SQLite real com payload criptografado |
| README, estrutura de repositório e testes | Atendido no MVP | Documentação, scripts Windows e suíte automatizada |
| Não enviar evidências pessoais para nuvem | Atendido no código revisado | Sem integração externa para processar evidências; servidor local por padrão |

As três pendências funcionais identificadas na revisão inicial foram implementadas na versão 1.1. O modo completo usa C#/EF Core; o modo Python continua independente. A IA precisa do Ollama e do modelo instalados, é opcional e pode produzir explicações incorretas. Esses requisitos de instalação e limites fazem parte da entrega, não são garantias de detecção de fraude.

## Validação da versão 1.1

- Suíte Python ampliada para QR Code, rotas internas autenticadas, encaminhamento para C# e isolamento da IA.
- Teste de integração C# aprovado com SQLite real: token, validação de entrada, salvamento opcional, criptografia, consulta e exclusão.
- Teste real `scripts/smoke_completo.py --with-ai` aprovado neste computador: QR de imagem fictícia, ciclo Python → C# → Python, histórico EF Core criptografado, leitura e limpeza e geração com Ollama/Qwen local.
- Modelo e executáveis ficam em `.tools`, ignorado pelo Git. O primeiro carregamento da IA exige mais tempo; a interface informa esse limite e preserva o resultado das regras em caso de falha.
- 27 testes Python e um teste C# de integração aprovados localmente. O CI inclui também o fluxo real dos serviços sem exigir o modelo de IA.
- A revisão visual da versão 1.1 ficou limitada pela conexão do navegador. Essa pendência foi resolvida na versão 1.2 em 6 de novembro: OCR, QR, análise com IA, histórico, desktop e formulário móvel foram conferidos no navegador. Consulte [ENTREGA.md](ENTREGA.md).

## Revisão antes da publicação

- Conferidos arquivos rastreados e nomes de arquivos do histórico Git: sem capturas pessoais, bancos de análises ou ambiente virtual versionados.
- Busca por padrões comuns de tokens e chaves privadas nas revisões Git não encontrou correspondências. É uma verificação limitada, não uma auditoria independente de segurança.
- Dados usados nos exemplos são fictícios.
- Histórico desativado por padrão; conteúdo criptografado quando solicitado. A chave fica na mesma conta local e não protege contra controle da conta.
- O e-mail de autoria dos commits faz parte do histórico público do Git.
- O upload do framework pode usar armazenamento temporário local; a documentação não promete processamento exclusivamente em RAM.
- Não há licença de reutilização escolhida pelo autor. Repositório público não equivale a concessão de uma licença de software livre.

## Limites da avaliação

Esta revisão compara o código com o roteiro identificado. Não é certificação de conformidade com LGPD, WCAG ou normas bancárias. Não houve auditoria externa, teste de invasão nem avaliação estatística da precisão das regras ou do OCR.

A publicação expõe o código e seu histórico no GitHub. O aplicativo continua sendo executado localmente; não há serviço web público hospedado.
