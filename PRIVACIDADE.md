# Privacidade

O ConfereAntes foi projetado para funcionar localmente.

## Dados processados

O usuário pode fornecer textos, imagens, links escritos, códigos Pix e nomes de destinatários. Esses dados são usados somente para produzir a análise solicitada.

O recebimento de uploads usa o mecanismo do framework, que pode utilizar arquivos temporários no computador conforme o tamanho do arquivo. O OCR lê os bytes em memória e o aplicativo não mantém um acervo das imagens recebidas. Não há rotina de envio das evidências para serviços externos.

## Histórico opcional

O histórico fica desligado por padrão. Quando o usuário marca a opção de salvar, um resumo da análise e trechos das evidências são criptografados e gravados em `%LOCALAPPDATA%\ConfereAntes\historico.sqlite3`.

A chave fica em `%LOCALAPPDATA%\ConfereAntes\historico.key`. Apagar essa chave torna o histórico existente ilegível. A criptografia não protege os dados de alguém que já tenha controle completo da conta do Windows.

O histórico pode ser apagado pela própria interface.

## Rede

Por padrão, o servidor escuta somente em `127.0.0.1`. Links informados são analisados como texto e não são acessados.
