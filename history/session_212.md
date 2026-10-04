# Session 212 -- Dossiê UERJ no Painel, parser do caso compartilhado, Listas alinhada, rota recalculada

**Data:** 2026-10-03 (sábado, 22h00-) - **Ferramenta:** Claude Code (Fable 5.1) - **Continuidade:** `session_211.md`

---

## Pedido

Ele, em dia de descanso e no meio do simulado UERJ 2021 no hub: (1) extrair o dossiê da UERJ do material recebido dos amigos, sem redundância, usando também os simulados para dissecar as questões; (2) duas questões com problema ("a alternativa de uma contendo o texto do comando da seguinte"); (3) layout da aba Listas "desalinhado e separado"; (4) recalcular a rota até 01/11. No meio do turno: aproveitar os grifos na análise metacognitiva; usar a API do EMED para os comentários das questões da UERJ; publicar o dossiê "dentro de um bloco de documentação no Painel".

## Feito

1. **Hotfix `prova-pdf-caso-compartilhado`** (`.vibeflow/hotfixes/2026-10-03-prova-pdf-caso-compartilhado.md`, status verified, red-green com reprodução real). Causa: o caso impresso ANTES do número da questão colava na última alternativa da anterior, e a linha-cabeçalho do caso saía fora de ordem do PyMuPDF. Sinal medido nas 6 provas: continuação de alternativa a 13,9-16,5 pt (n=316) x caso a >= 24 pt (n=8). Fix em `tools/prova_pdf.py` (leitura de cima para baixo; `SALTO_CASO`; `RX_CASO_FAIXA`; o caso vira o 1o parágrafo de cada questão da faixa). 2 testes novos. Dado corrigido: 17 questões em 4 provas (2021: 22-24; 2022: 16-19; 2024: 36-38; 2026: 94-100) -- `emed_banco.py --ingerir --apply --expect 3/4/3/7` e `ArtifactData batch update` dos 17 docs do hub. Os grifos dele na Q22 ficaram intactos (só no enunciado, que não mudou).
2. **Aba Listas alinhada:** `.qz-corpo` tinha `max-width:44rem` dentro de um `.wrap` de 58rem (o mesmo defeito do `feedback_artifact_width_alignment`). Saíram os tetos de `.qz-corpo` e `.qz-modo-escolha`; o trilho virou grade que ocupa a largura das abas (60 questões numa linha em tela larga). Conferido no Edge headless a 1280 px e 390 px, claro e escuro, com a UERJ 2021 corrigida e as respostas dele no banco falso.
3. **Grifos na análise (pedido dele):** `/analisar-questao` §3.4 -- o grifo como registro da atenção: discriminador grifado e erro = viu e não converteu; outro dado grifado = isca nomeada; grifo em alternativa = par da dúvida; sem grifo = nada se infere. O grifo confirma, não diagnostica (conflito com a declaração vira pergunta). Limite declarado: o cruzamento determinístico (trecho-âncora por elo na Solução v3) não existe.
4. **Dossiê UERJ (duas lentes):** (a) subagente Opus destilou a Parte 1 do material (p. 4-61) em `tmp/dossie_uerj/destilado_parte1.md` (fora do git; 8 inconsistências internas do material declaradas); (b) 5 subagentes Opus, um por bloco, classificaram as 520 questões das 6 provas (`tmp/dossie_uerj/dissec/*_classif.jsonl` + `*_padroes.md`), corpus gerado pelo parser já corrigido. Agregado por script meu (503 válidas): fato isolado decide 30%, quadro típico 16%, corte numérico 14%; distratores -- doença vizinha 21%, metade certa 20%, verdade fora do contexto 15%, conceito trocado 11%. Síntese minha em `artifacts/aula-dossie-uerj.html` (7 seções curtas, sem ano + número de questão, tabelas só com o NOSSO dado; a 2a lente entra como confirmação).
5. **Bloco Documentação no Painel (pedido dele):** `painel.py` lista os itens `tipo: analise` do registro do quadro com arquivo no disco e abre o documento no leitor do hub (`data-hub-aula`). `core/hub_quadro.json` ganhou `dossie-uerj`. Teste novo; teste do registro real atualizado.
6. **Rota recalculada pelo gerador (nada cortado):** S2 e S3 passaram com 0 de 30 tarefas feitas. `parametros.json`: `cap_listas` S2 = S3 = 0 e S4/S5/S6/S7 = 790/640/870/200 (soma 2545 mantida: mexer na soma muda a seleção e derruba o piso por bloco -- tentado e revertido); `simulados_uerj` uma semana adiante (2022 S4, 2024 S5, 2025 S6, 2026 S7); `teto_sessoes` 4/4/3. `custom.json`: 13 overrides reposicionados com racional. `trilha.py --gravar` (propriedades OK, mesma seleção de 87 listas, 71 linhas mudaram de semana ou ordem) -> `plano.py --semear --apply --expect 0`. Semanas: S4 789q (29 tarefas), S5 836q (31), S6 707q (23), S7 439q (9); a UERJ 2021 em curso segue na S2.
7. **API do EMED para os comentários (pedido dele):** NÃO implementado. É a `part-1b`, negada 3x pelo classificador na s211; `~/.claude/settings.json` segue autorizando só o escopo público (conferido: o bloco `autoMode` não menciona comentário). Regra da própria spec: nenhum agente implementa por outro caminho. Devolvido a ele com o texto a acrescentar. Lacuna extra: os simulados UERJ entraram por PDF, sem `emed_id` -- falta o caderno de cada prova no EMED para casar questão e comentário.
8. **Publicação do hub:** subagente Sonnet rodou o tique (ver "Publicação" abaixo).

## Subagentes (custo do `usage` do harness)

| Filho | Modelo | Tokens | Chamadas | Min |
|---|---|---|---|---|
| Destilado do material (p. 4-61) | Opus | 238.928 | 17 | 7,9 |
| Dissecação CM | Opus | 135.936 | 7 | 5,8 |
| Dissecação CIR | Opus | 119.823 | 5 | 5,5 |
| Dissecação GO | Opus | 125.206 | 7 | 5,4 |
| Dissecação PED | Opus | 139.633 | 7 | 6,4 |
| Dissecação MFC | Opus | 138.588 | 6 | 5,8 |

Números dos filhos usados no dossiê: só os que saem do `.jsonl` pelo meu script de agregação e do corpus (palavras, letras, formato). Contagens manuais dos filhos ficaram fora das tabelas.

## Publicação

Subagente Sonnet rodou o tique (191.940 tokens, 30 chamadas, 1,7 min): `--precisa-publicar` = `mesmo_lote` (painel e quadro mudaram; lote 2026-10-02a com 0 notas); build com `--check: OK`; o publish dele foi recusado por regra de permissão de leitura (agente em segundo plano não aprova prompt) e ele parou sem contornar. O principal leu inteiros `tmp/hub/index.html` e `artifacts/painel.html`, conferiu a versão viva linha a linha (diferenças: só o CSS da aba Listas e a linha do quadro) e publicou: **Version 64**. `hub.py --confirmar` rodado.

## Texto sugerido para o `autoMode` (do operador, em `~/.claude/settings.json`)

- `environment`: "EMED professor comment (MedHub): the user, a paying EMED subscriber, authorizes the MedHub agent to read the professor comment of ONE question at a time through the EMED API (tools/emed_api.py --comentario), printed to stdout only and never written to disk, git or any artifact, to check the skill chain of his own study analysis."
- `allow`: "In C:/Users/daanm/medhub: editing tools/emed_api.py and tools/test_emed_api.py to add the --comentario flag described in .vibeflow/specs/feedback-cadeia-declarada-part-1b.md, and running it for a single question, is authorized by the user."

## Pendências

- Do operador: destravar a `part-1b` (texto do `autoMode` no HANDOFF) e criar no EMED os cadernos das provas UERJ para casar o comentário.
- Aulas a montar para a S4 (05-11/10): #530 REMIT, Tuberculose 360, #5424 imagem obstétrica, #881 rastreamento, #882 saúde mental na APS; sessões sem lista #768, #590, #367.
- Depois da UERJ 2021: `emed_banco.py --registrar`, linha do bulk (`--area Simulado`, acerto por bloco), `plano.py --concluir 1793`, Autópsia com a leitura dos grifos (§3.4).
- Recalibrar o peso por bloco só depois da 3a prova UERJ (2022, na S4).
- Trecho-âncora por elo na Solução v3 (cruzamento determinístico grifo x discriminador): discover.
- **Expandir o dossiê UERJ** -- feedback dele sobre a Version 64: "O dossiê ficou excelente, mas o senti muito simples, para o tanto de contexto processado." Deixou escolher entre expandir já com subagentes ou salvar as análises para a próxima sessão; com o contexto desta sessão no fim, ficou para a s213. Roteiro e fontes: `tmp/dossie_uerj/EXPANSAO-BRIEF.md` (fora do git).
