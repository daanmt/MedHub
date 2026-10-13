# Spec: sprint-final-uerj -- part 1: a tentativa nova pede conexão nova ao banco (hotfix)

> PRD: `.vibeflow/prds/sprint-final-uerj.md` (Solution 6). Gerada em 13/10/2026 (s226).

## Objetivo

Depois de uma troca de versão do hub com a página aberta, a aba Listas (e a Teoria e a lista aberta) se recupera
sozinha, sem ele sair do artifact e voltar.

## Contexto

Evidência de 13/10 (prints dele): Version 108 recém-publicada, aba Listas em "Não consegui ler as listas. Tentar de
novo" com as 3 tentativas esgotadas; sair para o menu de artefatos do Claude Desktop e voltar carregou tudo. A
`assinarResiliente` (`core/templates/hub.html` ~l.1697) reassina com a MESMA `consulta()`, que fecha sobre o `db` obtido
uma vez (`QZ.db`, o `db` da Teoria e do Painel ao vivo); se a conexão morreu, as 3 tentativas usam a conexão morta.

## Definition of Done

1. Na 2ª tentativa em diante (e no "Tentar de novo"), a assinatura obtém o banco de novo por
   `window.claude.use("db")` antes de montar a consulta; a consulta passa a receber o `db` (`consulta(db)`), e os 4
   chamadores (listas, quadro, lista aberta, Painel ao vivo) usam o `db` recebido, nunca o capturado.
2. `QZ.db` é atualizado com o `db` novo quando a reconexão acontece (a gravação de respostas usa o mesmo).
3. Teste novo em `tools/test_hub_render.py` (`test_retentativa_pede_conexao_nova`): banco falso cuja 1ª conexão falha
   em toda leitura e a 2ª funciona -> a aba Listas e a Teoria carregam sem recarregar; conta 2 chamadas a `use("db")`.
4. O `ui_harness.html` ganha o modo `?leitura=conexao` (a 1ª conexão sempre falha) e `python tools/ui_capturas.py`
   com ele mostra as listas a 390 px sem erro de JS.
5. Artesania: os testes da part-1 de `hub-correcoes-pos-tema-v3` seguem verdes sem edição de expectativa; sem cor
   literal nova; suíte inteira verde.

## Escopo

`core/templates/hub.html`, `core/templates/ui_harness.html`, `tools/test_hub_render.py` (e `tools/test_hub_quadro.py`
só se o extrator `FUNCS_QD` precisar da assinatura nova), `docs/UI.md` (histórico).

## Anti-escopo

Pendências e grifos (leem por `claude.use("db")` próprio); escrita; qualquer layout.

## Decisões técnicas

- Reconectar só a partir da 2ª tentativa: a 1ª falha pode ser soluço do banco; pedir conexão nova a cada erro custa pouco
  mas mudaria o caminho feliz.
- Trade-off: se `use("db")` devolver `null` na reconexão, a tentativa conta como falha (vai para a espera seguinte).

## Riscos

- Dois ouvintes vivos se a conexão velha "voltar" -> o `soltar()` do ouvinte velho segue antes de reassinar (já é assim).
