# ConfereAntes

Comecei este projeto para ajudar a conferir uma mensagem ou cobrança antes de fazer um Pix. A ideia é comparar o que foi anunciado com o que chegou na conversa e chamar atenção para diferenças de valor, links estranhos e sinais comuns de golpe.

Ainda é um MVP. Por enquanto, a análise é feita com regras simples e roda no próprio computador. O resultado serve como alerta e não substitui a confirmação com a pessoa ou empresa por um canal oficial.

## O que já funciona

- comparação do texto do anúncio com a mensagem recebida;
- identificação de urgência, pedido de sigilo, senha ou acesso remoto;
- verificação do endereço escrito de um link, sem acessá-lo;
- comparação de valores em reais;
- pontuação de atenção acompanhada dos motivos encontrados.

## Executar localmente

Requer Python 3.11 ou superior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn confereantes.main:app --reload
```

Depois, abra `http://127.0.0.1:8000`.

## Testes

```powershell
pytest
```

## Privacidade

- O servidor usa `127.0.0.1` por padrão.
- O conteúdo analisado não é enviado para uma API externa.
- Capturas de tela e outros dados pessoais não fazem parte deste repositório.

## Próximos passos

- adicionar leitura local de capturas de tela;
- melhorar a comparação de nomes, valores e destinatários Pix;
- criar um histórico local opcional;
- preparar uma versão fácil de instalar no Windows.

