# ConfereAntes

Aplicativo local para analisar mensagens, links e cobranças Pix **antes do pagamento**. O objetivo é destacar inconsistências e sinais comuns de engenharia social sem abrir links suspeitos e sem enviar dados pessoais para serviços externos.

> O ConfereAntes oferece sinais de risco, não um veredito. Nenhuma análise substitui a confirmação pelos canais oficiais da empresa ou pessoa envolvida.

## Estado atual

Primeiro MVP:

- interface web executada somente no computador local;
- comparação entre o anúncio original e a conversa/cobrança recebida;
- análise de urgência, sigilo, pedido de credenciais e acesso remoto;
- inspeção segura do texto de links, sem abri-los;
- comparação de valores em reais entre as evidências;
- resultado com pontuação, nível de atenção e recomendações.

O OCR de capturas de tela será adicionado no próximo marco.

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

- O servidor escuta apenas em `127.0.0.1` por padrão.
- O MVP não envia conteúdo para APIs externas.
- Evidências pessoais não devem ser adicionadas ao repositório.
- Segredos e configurações locais devem ficar em `.env`, que está ignorado pelo Git.

## Marcos sugeridos

1. Interface e motor inicial de sinais de risco.
2. OCR local para capturas de tela.
3. Comparação estruturada de nomes, valores, domínios e destinatários Pix.
4. Histórico local opcional e criptografado.
5. Empacotamento para Windows e documentação de demonstração.

