# PRD: Hub -- integração e corte de passos (P13 + P14 + P08 v0)

> Generated via discover on 2026-10-05 (s216). Decisões do operador tomadas na própria discovery.

## Problem

O operador estuda pelo hub no celular e perde tempo em UI, não em estudo. Três dores medidas (`docs/MEDICAO-HUB-3-BLOCOS-2026-10-05.md`):

1. **Redundância.** O cronograma inteiro aparece duas vezes (92 tarefas no Painel e as mesmas 92 na aba Aulas; só 12 são de aula). A mesma regra mora em 2-3 lugares (2 leitores do `hub_quadro.json`, 2 renderizadores de ação, 3 réguas de semana). Uma tarefa concluída na aba Listas aparece resolvida em Aulas e aberta no Painel.
2. **Painel velho.** O Painel é uma foto gerada no publish. A página já grava no `db` do artifact tudo o que ele faz (notas do lote em `sessoes/<sessao>/notas`, `respostas/*`, `listas/*.status`, `quadro/*`) e o Painel ignora. Ele lê "Hoje: 0" depois de 150 cards; a correção depende de um tique manual no PC ("desconfio que o dashboard não está syncado", s214).
3. **Gesto a mais.** Assinar um documento só pinta o botão; concluir uma lista só troca o status; o "voltar" do leitor vai sempre para Aulas, mesmo quando o documento foi aberto pelo Painel. Cada conclusão exige um toque extra para sair da página.

Palavras dele (05/10): *"os ganhos agora são de integração, remoção de redundâncias, cortar passos desnecessários, e priorizar 95% do tempo do usuário estudando, e não tendo dificuldades com a UI e uma UX ruim"* (P15, régua do backlog até 01/11).

## Target Audience

O operador, sozinho, no celular (390 px), entre blocos de estudo. Prova UERJ em 01/11/2026: nada que tire tempo de estudo nem mexa no player de cards.

## Proposed Solution

Reorganizar o hub em 4 abas sem informação repetida, fazer o Painel somar ao vivo o que a página já gravou, e fazer todo gesto de conclusão (assinar, marcar resolvida) fechar a página e devolver o operador à aba de origem.

- **Abas, nesta ordem: Painel | Teoria | Listas | Cards** (decisão dele: "questões geram os cards", então Listas vem antes de Cards). Painel = performance + cronograma + ritmo + Documentação. Teoria = só tarefas de aula e aulas ligadas a tarefas, com Biblioteca do que foi concluído. Listas e Cards = mão na massa.
- **Biblioteca só daqui em diante:** nada concluído some mais; as 5 aulas já arquivadas voltam sob pedido, uma a uma.
- **Documentação (Dossiê, Autópsias) só no Painel.**
- **Hoje ao vivo, v0 = só soma, não substitui:** o Painel mostra o número publicado mais o que a página gravou depois do publish (cards com nota, questões respondidas, listas resolvidas). Teto, saldo e registro oficial seguem do tique. O P09 (dia de estudo x relógio) não bloqueia este v0.
- **Concluir = fechar e voltar:** após gravar com sucesso (assinatura, lista resolvida), o leitor fecha e a aba de ORIGEM reaparece com o item recém-concluído marcado. Falha de gravação mantém a página aberta com o status visível (o rascunho já fica no aparelho).

## Success Criteria

1. Um dia inteiro de uso sem tique de backend em que o Painel mostre o volume de hoje certo (publicado + ao vivo), conferido contra `fsrs_queue`/`emed_banco` no fechamento.
2. Nenhuma tarefa aparece em dois estados (resolvida em uma aba, aberta em outra) na mesma abertura do hub.
3. Assinar ou concluir devolve à aba de origem sem toque extra, no celular, em todas as origens (Painel, Teoria, Listas).
4. O cronograma de 92 tarefas aparece uma vez (Painel); Teoria lista só as 12 tarefas de aula e suas aulas.
5. `mesmo_lote` passa a subir só `painel.html` (~38 KB) quando uma lista é concluída, e não mais o `index.html` (~341 KB) -- medição do E01.
6. Suíte verde; testes nomeados na medição §3 reescritos, não apagados.

## Scope v0

Fatias F1-F4 da medição (P13), mais F5 (P14) e F6 (P08 v0), em uma sessão de engenharia, nesta ordem:

- **F1 Teoria só com teoria:** `secoes_do_quadro` (`hub.py:390-474`) mantém só tarefa de aula e tarefa com aula ligada; rótulo "Teoria"; `data-aba="aulas"` intacto (sem mexer em `ABAS`, hash, `localStorage`).
- **F2 Painel lê `listas/*`:** `_html_tarefa` emite `data-tarefa`/`data-slug`; `marcarListas` sai de `iniciarQuadro` e é aplicado também ao iframe do Painel. Sai no MESMO publish da F1 (senão o P06 regride).
- **F3 Biblioteca daqui em diante:** acaba o `git mv` para `artifacts/arquivo/`; "Outras aulas" + "Concluídas" viram "Biblioteca" (mesmo id `hub-quadro-feitas`); ritos `revisar.md:239`, `aula-base.md:82` e `_doc` do registro atualizados.
- **F4 Listas -> aula que prepara:** JSON derivado de `ligacoes_do_quadro` num `<script>` próprio; `qzItemLista` ganha "abrir aula".
- **F5 Concluir = fechar e voltar (P14):** assinatura (`hub.html` ~902) e `qz-concluir` (~1921) chamam, após o `.then` de sucesso, o retorno à aba de origem (guardar a origem ao abrir o leitor; hoje `fecharAula` volta sempre para Aulas). Item recém-concluído marcado ao voltar. ~30 linhas, ~4 testes.
- **Regra P09 (decisão dele, 05/10):** um lote de cards conta inteiro no dia em que recebeu a 1ª nota, mesmo que termine depois da meia-noite; o FSRS guarda o horário real. Teto do dia e Painel passam a contar por essa regra (`consumo_hoje` do export e `painel.py`). Entra nesta sessão porque F6 mostra o número ao lado do publicado e os dois precisam concordar.
- **F6 Hoje ao vivo v0 (P08):** o Painel embute `sessao` do lote no ar e o `publicado_em`; ao abrir, a página conta no `db` as notas de `sessoes/<sessao>/notas`, as `respostas/*` de hoje e as `listas/*` resolvidas DEPOIS do `publicado_em` e mostra "+N desde o publish" ao lado do número publicado. Nunca altera teto, saldo nem o número publicado. Regra de dupla contagem = só o que tem timestamp posterior ao publish.
- **Reordenar as abas** para Painel | Teoria | Listas | Cards (só a ordem dos botões e do `ABAS`; ids e hashes intactos).
- Conferência em navegador real a 390 px antes do publish (regra s211) e republicação na URL fixa do hub.

## Anti-scope

- Fusão Cards + Listas numa aba (mexe no player e no teclado do drill).
- Resumos dentro da Teoria (P03): conteúdo novo, ~160 mil tokens de publish.
- Pendências no Painel (P10), edição de aulas "como no Notion" (P02), reabrir as 5 aulas arquivadas.
- "Hoje ao vivo" que SUBSTITUA o número publicado. (O P09 foi decidido: contar pelo dia em que o lote começou.)
- Dado novo no `db`, regra nova de `capabilities`, mudança no `--record-lote` ou no tique do `/hub-backend`. (O export da fila muda só no `consumo_hoje`, pela regra P09.)
- Unificar os grifos de questões e aulas (E07, pós-01/11).
- Backend próprio (P11, pós-01/11).

## Technical Context

- Hub = 1 artifact fixo (`core/templates/hub.html`, 2.019 linhas; `tools/hub.py` 1.223 linhas; `tools/painel.py`). Abas por `data-aba` em `:root`, hash e `localStorage`; `ABAS = ["painel","aulas","cards","questoes"]` (`hub.html:410`). O Painel é um iframe `srcdoc` carregado uma vez (`carregarPainel`, `hub.html:1395`).
- `db` do artifact já declarado (regras `sessoes`/`quadro` interact; `listas`/`questoes`/`respostas`/`analises` admin). A página já lê `listas/*` para o quadro (`hub.html:1348-1361`) e grava notas, respostas, status e assinaturas. Nenhuma capability nova.
- Backend = tique manual `/hub-backend` (`hub.py --precisa-publicar` decide `nada | mesmo_lote | nova_fila`); a projeção publicada é a base da próxima decisão. F6 não muda esse rito.
- Gargalo E01: cada publish que muda `index.html` exige ler ~90 mil tokens. F2 faz lista concluída deixar de mudar o index.
- Padrões: testes em `tools/test_hub*.py` e `tools/test_painel.py` (lista dos que caem na medição §3); `auto_check.py --changed` antes de reportar; hub conferido em navegador real (`project_conferir_tela_no_navegador`); design minimalista; celular sem nowrap longo, `min-width:0`.
- Dono do backlog: `/ai-eng` (`~/ai-eng/HANDOFF-MEDHUB-produto-2026-10-05.md`, adendos s215 e s216). Backlog: `docs/BACKLOG-PRODUTO.md` (P08, P13, P14, P15, E01).

## Open Questions

- Regra P09 no `consumo_hoje`: o dia do lote = dia da 1ª nota gravada na coleção `sessoes/<sessao>/notas` ou o dia do export? Recomendação: 1ª nota.

- F6: o "hoje" das questões respondidas conta pelo `respondida_em` da página; se um dia ele responder no EMED fora do hub, o ao-vivo não vê (já é assim no publicado). Aceito como limite declarado.
- F5: ao voltar da assinatura de um documento aberto pelo Painel, o iframe do Painel precisa re-marcar o item sem recarregar a foto -- confirmar no spec se `marcarListas` (F2) cobre documentos ou só listas.
