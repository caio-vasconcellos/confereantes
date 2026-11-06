# Segurança

[English](docs/en/SECURITY.md) · [Português](SEGURANCA.md)

## Relatar um problema

Não publique evidências pessoais, chaves Pix reais, senhas, tokens ou códigos de verificação em uma issue.

Ao relatar uma falha, use apenas exemplos fictícios e informe a versão do Python, do navegador e do ConfereAntes.

## Decisões de proteção

- servidor restrito a `127.0.0.1` por padrão;
- hosts aceitos limitados a `localhost`, `127.0.0.1` e ao host de testes;
- cabeçalhos de segurança e política de conteúdo aplicados às respostas;
- imagens limitadas por tipo, tamanho e quantidade de pixels;
- textos limitados antes da análise;
- links nunca são abertos pelo motor;
- histórico desativado por padrão e conteúdo criptografado quando salvo;
- documentação interativa da API desativada na versão local.
- API C# e processador interno autenticados com token efêmero, gerado pelo iniciador;
- clientes internos limitados a loopback, com proxy externo desativado;
- IA opcional recebe somente rótulos de regras e recomendações, sem evidências originais;
- saída da IA escapada no HTML e sem poder de alterar a pontuação;
- QR Code decodificado sem navegar no destino; múltiplos códigos são recusados.
- formulários e uploads exigem token CSRF por processo, distinto do token entre serviços;
- o cliente descarta saídas de IA fora do formato, truncadas ou contendo algumas recomendações inseguras conhecidas; isso não é garantia de correção semântica;
- links e códigos Pix malformados recebem alertas, sem navegação ou pagamento.

## Escopo

O aplicativo não substitui confirmação com banco, empresa, plataforma ou pessoa envolvida. Ele aponta inconsistências; não certifica pagamentos.
