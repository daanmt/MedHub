---
status: aprovado-escopo
sessao: s196
data: 2026-09-25
---

# PRD — Aba "Análise" no MedHub HUB

## Problema
A análise de listas e simulados vive no chat e no `ipub.db` (`questoes_erros`): o operador não revê a cadeia de raciocínio quebrada depois, nem diz se concorda com o diagnóstico do erro. Sem esse retorno, a análise não se calibra (racional declarado > inferido, memória `feedback_usuario_declara_racional_erro`).

## Decisões do operador (25/09/2026)
- **Entrada = chat, como hoje.** Ele traz o bloco (acertos, erradas, chutes, racional) e o agente analisa (`/analisar-questao`); a página só **mostra** e **coleta veredito**. Nenhum agente disparado pela página (classificador barrou isso na s194).
- **Histórico = só daqui para frente.** A aba nasce vazia e cresce a cada lista/simulado analisado a partir da s196.
- **Design = o do hub:** minimalista, limpo, formatação flexível (grades, chips, `<details>`), nunca parágrafo longo. Cabe em tela de celular.

## Escopo
1. **4ª aba "Análise"** no hub (`core/templates/hub.html`), ao lado de Painel / Aulas / Cards.
2. **Cartão por sessão** (lista ou simulado): tema/área, data, acerto `N/total`, sólidas × chutes × erradas, link da lista.
3. **Por erro, a cadeia em degraus** (1 linha cada): o que a questão pedia → habilidade sequencial onde quebrou (elo) → o dado que excluía a marcada (discriminador) → armadilha → card(s) gerado(s) (`#id`).
4. **Veredito do operador por erro:** `concordo · discordo · em parte` + campo curto opcional. Grava no `db` do hub (`analise/<erro_id>`, regra `write: interact`).
5. **Ingestão do veredito:** o tique do `/hub-backend` lê `analise/*` e grava em tabela local `analise_vereditos (erro_id, veredito, nota, ts)`. "Discordo" com nota vira item para eu reabrir a análise (e, se preciso, reforjar o card) na próxima sessão de estudo.
6. **Faixa de padrões:** contagem dos padrões de erro (discriminador que exclui, ancoragem no número, enunciado negativo…) nas sessões da aba, com tendência simples (↑/↓ vs sessão anterior).

## Fora do escopo (anti-escopo)
- Formulário de entrada de questões no celular.
- Importar os 1.087 erros antigos.
- Análise automática disparada pela página ou pelo tique.
- Qualquer mudança na aba Cards/Aulas/Painel além da navegação.

## Dados (a especificar no gen-spec)
- Ligar erro -> sessão: `questoes_erros` não tem vínculo com `sessoes_bulk`. Opção preferida: coluna `sessao_bulk_id` (nullable, preenchida pelo `insert_questao.py --sessao`), mais `racional_declarado` e `incerteza` (chute) se ainda não persistidos.
- Export para o hub: `hub.py --build` ganha `analise.json` (sessões desde a s196 + erros + cadeia + cards), igual ao `lote` dos cards.
- Capabilities do hub: acrescentar `{path: "analise", write: "interact"}` (só o agente principal publica a declaração, uma vez).

## Definition of Done (rascunho)
- [ ] Aba Análise renderiza o cartão de 1 sessão real, com erros em degraus, no celular sem scroll horizontal.
- [ ] Veredito gravado no `db` e lido pelo tique para `analise_vereditos` (teste com db falso).
- [ ] `insert_questao.py` persiste o vínculo erro -> sessão; teste cobre.
- [ ] `hub.py --check` valida o `analise.json`; `test_hub` verde.
- [ ] Nenhum parágrafo de prosa na aba (grade/chips/details).

## Próximo passo
`/vibeflow:gen-spec hub-aba-analise` -> implementar na próxima sessão de engenharia; a 1ª lista analisada depois disso (DMG #26 ou Pediatria #96) é o caso de aceitação.
