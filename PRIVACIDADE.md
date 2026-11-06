# Privacidade

[English](docs/en/PRIVACY.md) · [Português](PRIVACIDADE.md)

O ConfereAntes foi projetado para funcionar localmente.

## Dados processados

O usuário pode fornecer textos, imagens, links escritos, códigos Pix e nomes de destinatários. Esses dados são usados somente para produzir a análise solicitada.

O recebimento de uploads usa o mecanismo do framework, que pode utilizar arquivos temporários no computador conforme o tamanho do arquivo. O OCR lê os bytes em memória e o aplicativo não mantém um acervo das imagens recebidas. Não há rotina de envio das evidências para serviços externos.

## Histórico opcional

O histórico fica desligado por padrão. Quando o usuário marca a opção de salvar, um resumo da análise e trechos das evidências são criptografados e gravados em `%LOCALAPPDATA%\ConfereAntes\historico.sqlite3`.

A chave fica em `%LOCALAPPDATA%\ConfereAntes\historico.key`. Apagar essa chave torna o histórico existente ilegível. A criptografia não protege os dados de alguém que já tenha controle completo da conta do Windows.

O histórico pode ser apagado pela própria interface.

No modo completo, a API C# mantém um histórico separado em `%LOCALAPPDATA%\ConfereAntes\api\historico.db`, com EF Core e payload protegido por ASP.NET Data Protection. As chaves ficam no subdiretório `keys`; as mesmas limitações de acesso à conta se aplicam. O histórico Fernet do modo Python continua independente e não é migrado automaticamente.

## Explicação opcional por IA

Quando solicitada, a explicação usa Ollama local com o modelo `qwen2.5:1.5b`. O prompt contém somente títulos de alertas, recomendações genéricas, nível e pontuação. O aplicativo não inclui nomes, textos originais, URLs ou chaves Pix no prompt. A explicação não é salva no histórico. A instalação inicial do motor e o download do modelo requerem internet; a inferência usa o servidor de loopback. Execute pelo script `iniciar-ia.ps1` para desativar recursos cloud do Ollama.

## Rede

Por padrão, o servidor escuta somente em `127.0.0.1`. Links informados são analisados como texto e não são acessados.
