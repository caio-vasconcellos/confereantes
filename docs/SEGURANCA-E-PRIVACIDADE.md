# Segurança e privacidade

[Português](SEGURANCA-E-PRIVACIDADE.md) · [English](SECURITY-AND-PRIVACY.md)

O ConfereAntes ajuda a revisar informações; não autoriza pagamentos e não confirma a identidade de uma pessoa ou empresa. Um resultado baixo não prova que a cobrança é legítima. O CRC do Pix confirma a integridade do código, não a titularidade da chave.

## Dados locais

- A aplicação escuta em `127.0.0.1` por padrão.
- Textos, imagens, links escritos e códigos Pix não são enviados a um serviço de análise externo.
- Links são inspecionados como texto e nunca são abertos pelo motor.
- Uploads podem usar arquivos temporários do framework. As imagens não formam um acervo do aplicativo.
- Instalação de dependências e download do modelo exigem internet; a análise usa os componentes locais já instalados.

## Histórico

O histórico fica desligado até o usuário marcar a opção de salvar. O conteúdo é criptografado antes de entrar no SQLite.

- modo Python: `%LOCALAPPDATA%\ConfereAntes\historico.sqlite3` e `historico.key`;
- modo C#: `%LOCALAPPDATA%\ConfereAntes\api\historico.db` e chaves em `api\keys`.

Os históricos são independentes. Apagar uma chave pode tornar os registros ilegíveis. Como as chaves ficam no mesmo perfil do Windows, a criptografia não protege contra alguém que já controla essa conta.

## Explicação local

Quando solicitada, a explicação envia ao Ollama somente os títulos dos alertas, recomendações genéricas, nível e pontuação. Textos originais, nomes, links e chaves Pix não entram no prompt. A resposta não é guardada no histórico, não altera a pontuação e pode estar errada.

## Proteções da interface

O projeto limita tamanho de textos, arquivos, imagens e conteúdo de QR Code. Formulários usam proteção CSRF; a comunicação entre C# e Python usa outro token. Respostas incluem cabeçalhos de segurança e o HTML escapa o conteúdo exibido. Essas medidas reduzem riscos, mas não substituem uma auditoria de segurança.

## Relatar um problema

Use exemplos fictícios. Não publique capturas pessoais, chaves Pix reais, senhas, tokens ou códigos de verificação em issues. Inclua as versões do aplicativo, do Python e do navegador e descreva como reproduzir o erro.
