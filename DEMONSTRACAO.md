# Demonstração do ConfereAntes

Use somente dados fictícios. Não faça pagamentos durante a demonstração.

## Abrir

1. Execute `scripts/iniciar-ia.ps1` se quiser a explicação generativa. O modelo exigido é `qwen2.5:1.5b`.
2. Em outro terminal, execute `scripts/iniciar-completo.ps1`.
3. Acesse `http://127.0.0.1:8000`.

## Percurso de cinco minutos

1. Clique em **Testar com exemplo**. O contador passa a 02/02 e a seção complementar abre.
2. Confira os valores fictícios de R$ 1.850,00 e R$ 2.150,00 e os nomes diferentes.
3. Marque a explicação local, se o motor estiver ativo, e clique em **Conferir agora**.
4. Apresente o nível alto, a pontuação e as recomendações de cada alerta. Explique que pontuação não significa probabilidade de fraude.
5. Mostre o trecho gerado por IA e o aviso de que ele não define a pontuação.
6. Faça nova análise com dois textos iguais: `Produto por R$ 100,00. Retirada presencial.`. O resultado baixo também pede confirmação da origem.
7. Mostre o campo de captura de imagem e a leitura de QR Code. O conteúdo aparece para revisão, sem abrir links.
8. Se quiser demonstrar persistência, salve somente a análise fictícia e abra **Arquivo local**.
9. Use **Imprimir ou salvar em PDF** para abrir a impressão do navegador e escolher PDF.

## Explicar a arquitetura

- Python recebe imagens, executa OCR/QR e calcula os alertas.
- C# orquestra a análise e registra o histórico pelo EF Core.
- SQLite guarda o payload protegido.
- Ollama explica rótulos e recomendações sem receber os textos originais.

## Encerrar

Use Ctrl+C nos terminais do aplicativo e da IA. O iniciador completo encerra a API que abriu.

Para repetir a validação funcional sem usar o histórico pessoal, execute `python scripts/smoke_completo.py --with-ai` com as portas do aplicativo livres e o Ollama ativo. Sem modelo, retire `--with-ai`.
