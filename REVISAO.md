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
| Ler QR Code de uma imagem | Pendente | OCR não equivale a decodificação de QR Code |
| Identificar sinais de engenharia social | Atendido no MVP | Regras de urgência, sigilo, credenciais e acesso remoto |
| Relatório explicativo | Atendido com regras | Evidências, recomendações e impressão pelo navegador |
| IA generativa local para explicações | Pendente | O OCR usa reconhecimento de imagem; as explicações atuais não são geradas por LLM |
| API em C# e processamento em Python | Parcial | Backend atual em Python/FastAPI; sem API ASP.NET Core |
| SQLite e histórico local | Atendido no MVP | Salvamento opcional com conteúdo criptografado |
| EF Core | Pendente | Acesso ao SQLite atual pela biblioteca Python |
| README, estrutura de repositório e testes | Atendido no MVP | Documentação, scripts Windows e suíte automatizada |
| Não enviar evidências pessoais para nuvem | Atendido no código revisado | Sem integração externa para processar evidências; servidor local por padrão |

O resultado é um MVP publicável como projeto em desenvolvimento, mas ainda não corresponde a todo o roteiro original de IA generativa e C#.

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
