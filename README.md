# ConfereAntes

Comecei este projeto para ajudar a conferir uma mensagem ou cobrança antes de fazer um Pix. A ideia é comparar o que foi anunciado com o que chegou na conversa e chamar atenção para diferenças de valor, destinatário, links estranhos e sinais comuns de engenharia social.

O ConfereAntes roda no próprio computador. Ele não abre links, não acessa bancos e não envia as evidências para uma API externa. O resultado é um alerta explicável, não uma garantia de que uma cobrança seja legítima ou fraudulenta.

Esta versão inclui o processador Python, leitura de QR Code, API C# com EF Core/SQLite e explicações opcionais com IA generativa local. Veja [como executar o modo completo](ARQUITETURA.md) e a [revisão do roteiro](REVISAO.md).

## O que a versão 1.1 faz

- recebe texto ou capturas do anúncio e da conversa;
- extrai texto das imagens com OCR local e permite revisão;
- compara valores e nomes de destinatários;
- identifica pressão, sigilo, pedido de credenciais e acesso remoto;
- inspeciona o endereço escrito de links sem acessá-los;
- valida a estrutura e a integridade CRC de um Pix copia e cola;
- mostra os motivos da pontuação e uma recomendação para cada alerta;
- salva análises apenas quando solicitado, usando histórico local criptografado;
- permite imprimir o resultado ou salvá-lo como PDF pelo navegador.
- decodifica QR Code de uma imagem sem abrir o conteúdo;
- registra análises pela API C# no modo completo;
- pode gerar uma explicação dos alertas com Ollama no próprio computador.

## Instalação no Windows

Requer Python 3.11 ou superior.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\configurar.ps1
```

O OCR é instalado junto com o projeto e usa modelos locais. A primeira leitura pode demorar um pouco mais enquanto o motor é carregado.

## Executar

```powershell
.\scripts\iniciar.ps1
```

O navegador abre em `http://127.0.0.1:8000`. O servidor não é exposto para outros computadores da rede.

Para usar também a API C# e o histórico EF Core, instale o SDK .NET 10 e execute:

```powershell
.\scripts\iniciar-completo.ps1
```

A IA é opcional. Inicie o Ollama com `scripts\iniciar-ia.ps1`, instale uma vez o modelo com `ollama pull qwen2.5:0.5b` e marque a opção de explicação no formulário. A análise por regras funciona sem o modelo. Detalhes de configuração estão em [ARQUITETURA.md](ARQUITETURA.md).

## Desenvolvimento

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[ocr,dev]"
pytest
confereantes
```

## Privacidade

- O aplicativo não mantém um acervo de imagens. O recebimento do upload pode usar arquivos temporários gerenciados pelo framework; o OCR trabalha com os bytes lidos.
- O histórico é desativado por padrão.
- Quando ativado, o histórico fica em `%LOCALAPPDATA%\ConfereAntes`.
- O conteúdo de cada análise é criptografado antes de ser salvo no SQLite.
- No modo completo, a API usa um banco próprio em `%LOCALAPPDATA%\ConfereAntes\api`; o histórico anterior do modo Python não é migrado automaticamente.
- A chave de criptografia permanece no mesmo perfil do Windows; ela protege o banco contra leitura casual, mas não contra alguém que já controla a conta do usuário.
- Evidências reais nunca devem ser adicionadas ao Git.

Mais detalhes estão em [PRIVACIDADE.md](PRIVACIDADE.md) e [SEGURANCA.md](SEGURANCA.md).

## Limites

- OCR pode errar; revise sempre o texto extraído.
- A comparação de nomes é aproximada e pode gerar alertas indevidos.
- O aplicativo não consulta titularidade de chave Pix nem reputação de domínio.
- Um resultado de risco baixo não comprova legitimidade.

## Testes

```powershell
pytest
```

Os testes cobrem o motor de risco, parser de Pix, histórico criptografado e rotas web. O GitHub Actions executa a suíte automaticamente em cada envio.

Os testes adicionais cobrem QR Code real, isolamento do cliente de IA e persistência da API C#. Para estes últimos: `dotnet test api/ConfereAntes.Api.Tests`.

## Estrutura

```text
src/confereantes/
├── main.py          # rotas e validações web
├── risk_engine.py   # regras explicáveis
├── pix.py           # leitura do Pix copia e cola
├── ocr.py           # validação de imagem e OCR local
├── history.py       # histórico SQLite criptografado
├── templates/       # páginas HTML
└── static/          # CSS e JavaScript
```
