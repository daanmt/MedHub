# Spec: hub-correcoes-pos-tema-v3 -- part 1: abas que se recuperam sozinhas (+ chip e marca)

> PRD: `.vibeflow/prds/hub-correcoes-pos-tema-v3.md` (itens 1, 4 e 5). Gerada em 13/10/2026 (s226).
> Decisão das Open Questions (minha, salvo redireção dele): **medir e retentar na mesma spec**.

## Objetivo

Tocar em Listas ou Teoria nunca mais deixa a tela presa em "Não consegui ler": a página tenta de novo sozinha,
diz que está carregando e, se o banco seguir fora, oferece **Tentar de novo**.

## Contexto

`iniciarQuestoes` (`core/templates/hub.html` ~l.1903) assina `listas` uma vez (`QZ.iniciado = true`) e o callback
de erro só escreve a mensagem; tocar na aba de novo não refaz nada. O quadro da Teoria (~l.1835) engole o erro em
silêncio, e as assinaturas da lista aberta (~l.2027-2038: `questoes`, `respostas`, `analises`) só avisam "Recarregue
a página". O gatilho real não foi medido (palpite: falha momentânea ou troca de versão do artifact com a página aberta).

## Definition of Done

1. Existe UMA função de assinatura resiliente no hub (`assinarResiliente(ref, onDados, opts)` ou equivalente) e as
   assinaturas `listas` (aba Listas), `quadro` (Teoria) e `questoes`/`respostas`/`analises` (lista aberta) passam por
   ela -- conferível por `grep` (nenhum `.onSnapshot(` direto nesses cinco pontos).
2. Erro de leitura: `console.warn("[hub] leitura <colecao> falhou", codigo, tentativa)` e nova assinatura com espera
   crescente (1 s, 2 s, 4 s; 3 tentativas); durante a espera a área mostra "Carregando…"; esgotadas, mostra a mensagem
   com um botão **Tentar de novo** que reinicia o ciclo. Reabrir a aba com a assinatura morta também reinicia.
3. No banco falso do `core/templates/ui_harness.html`: com `leitura=1x` a aba Listas e a Teoria aparecem sem recarregar
   em até 5 s; com `leitura=0` aparece o botão e, trocado o banco para bom, o toque carrega -- teste novo em
   `tools/test_hub_render.py` (`test_listas_se_recuperam_da_falha_de_leitura` e
   `test_botao_tentar_de_novo_reassina`) verde, mais a suíte inteira.
4. Listas: nenhum chip para o estado `capturada`/"pronta"; "em curso" mostra `respondidas/total`; "resolvida" segue
   com ✓ -- teste em `tools/test_hub_render.py`.
5. `.hub-marca` em `1.375rem`, "Hub" segue `var(--rosa)`.
6. Artesania: nenhuma cor literal nova fora do `tema.css` (o teste de cor literal da s225 segue verde), nenhuma
   violação dos Don'ts de `.vibeflow/conventions.md`, e `python tools/ui_capturas.py` sem rolagem horizontal a 390/768/1280.

## Escopo

- `core/templates/hub.html`: a função resiliente, as 5 assinaturas, o estado "Carregando…"/botão, chip, marca.
- `core/templates/ui_harness.html`: só se o `leitura=1x` não cobrir a coleção `quadro` (ajuste mínimo).
- `tools/test_hub_render.py`: os testes do DoD 3 e 4.
- `docs/UI.md`: linha no histórico + achado fechado.

## Anti-escopo

- As assinaturas do Painel ao vivo (`painelVivo`, `LISTAS_VIVAS`), das pendências e dos grifos: degradam em silêncio
  hoje e seguem assim (o número publicado vale). Ficam para depois, se o log mostrar falha ali.
- Qualquer mudança de layout além de chip e marca. Paleta, tipografia.
- Retentativa de ESCRITA (gravação de resposta já tem o espelho local).

## Decisões técnicas

- **Retentar por reassinatura, não por releitura `get()`**: o `onSnapshot` é o que a página usa em todo lugar e mantém
  o vivo; trade-off: um unsub a guardar por assinatura (guardar em `QZ.unsubs`/estado da aba).
- **3 tentativas com 1/2/4 s**: cobre falha momentânea (< 7 s) sem martelar o banco; depois o botão (controle dele).
- **Log no console com código**: é a medição pedida na Open Question 1; nada vai para o banco (não criar coleção de log).
- `QZ.iniciado` passa a significar "assinatura viva", não "já tentei uma vez".

## Padrões aplicáveis

- `docs/UI.md` §4 (semântica: o botão é ação = ciano; aviso = âmbar), §7 (contratos travados por teste), §8 (conferência).
- Padrão novo: assinatura resiliente do hub -- registrar em `docs/UI.md` §5 (componentes) para as próximas abas.

## Riscos

- **Assinatura duplicada** (reabrir a aba durante a espera cria 2 listeners e a lista pisca/duplica) -> um único estado
  por coleção (`viva | esperando | morta`) e unsub antes de reassinar; teste conta os listeners no banco falso.
- **Ordem `questoes` x `respostas`** (achado do PRD: Q1 aparece como nova) -> não corrigir aqui além de não piorar;
  se a retentativa reordenar, o teste do espelho local `medhub.respostas.<lista>` pega.
- O banco falso não reproduz a falha real -> o log fica no console para a 1ª ocorrência real.
