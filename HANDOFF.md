# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-12 (madrugada) -- **S180 (ESTUDO)**: Simulado 9 **86/100**, 14 erros registrados, 13 cards (11 reforjados), **override do modal** nomeado e medido, Raio-X dos 9 simulados publicado. Volume 7.126 -> **7.226**.*

> 🔴 **ENAMED e AMANHA (dom 13/09) -- termometro, nao alvo.** Sabado 12/09 = **descanso + cards**, sem questoes (decisao do operador). Permit de engenharia **CONSUMIDO**; janela 4 so com permit novo, verbatim, via `/ai-eng`. 🆕 **A regra da s179 (racional declarado) ja rendeu:** foi o racional dele nas 14 erradas que tornou o override do modal mensuravel.

## > Proximo passo imediato

1. 🃏 **Sabado (descanso): fila de 86 vencidos** (14 atrasados + 8 erros frescos de Diarreia/Urologia + 64 de hoje -- pico das 16 notas 1 da s179) e depois **intake dirigido aos dormentes**: Anemias Hemoliticas (71d, 60%), Olho Vermelho (71d), Potassio + Acido-Base (64d), DM Cronicas (63d), Pneumo Intensiva (19 novos), Hepatites Virais (22 novos), Meningites (20 novos). Um `--tema` por bloco de 15. **Teto:** contrato = 90 em divida; 150 e defensavel sem questoes, **200 vira divida na terca**. Os 14 de relearning da s179 levam nota normal (outro dia).
2. 🎯 **Domingo: ENAMED.** Uma instrucao: **quando restarem duas, marca a primeira.** Regra dos dois finalistas = `docs/PLAYBOOK_EXECUCAO_PROVA.md` item 7. Cards do dia 13-14 reaparecem dia 15 como atrasados (F98) -- deixar.
3. 📝 **`registrar_sessao_bulk` da lista de Diarreia de 09/09** -- **3a sessao seguida** sem feitas/acertos. Registrar ANTES de analisar qualquer questao nova.
4. 🗓️ **Segunda 14/09 = DECISAO:** rescope da grade para o formato UERJ (Clinica Medica 27% -> 20%, **MFC 6,7% -> 20% com zero questoes/cards/erros**), abertura da frente MFC (Gusso + Duncan) e **quais ~460 dos 676** nunca-introduzidos entram ate 01/11. Insumo: `artifacts/raio-x-simulados.html` §3.
5. 🔴 **Polipos e Neoplasias Intestinais NAO TEM RESUMO** (`[SEM-LASTRO]` da s180): 19 erros, 32 cards, 4a maior fraqueza, somou a Q28 do S9. + Farmacodermias (DRESS falhou 2x na s179) tambem sem `.md`. **Conteudo, nao card.**
6. 🔴 **Passivo de cards: `reforja --fila` = 272 abertas.** Triar e do operador (`--fechar` re-verifica; `--descartar` = "nao era defeito"; discriminador legitimo sai por `--descartar`).
7. 📚 **Backlog de conteudo:** 6 temas do Simulado 8 sem resumo + s172 (Dist. Resp. Neonatais, Infeccoes Congenitas, cerclagem). **395 PDFs / 136 `.md` / 327 orfaos**.

## Fila de engenharia -- **TIER 0 e TIER 1 ZERADOS**. Inventario: `docs/MEMORIA-AUDITORIA.md §11`

- ⚰️ **Janelas 1-3 (s176/s177/s178):** 0.0 a 0.7 e 1.1 a 1.9c + riders F96/F97. Itens e lapides em `docs/MEMORIA-AUDITORIA.md §11`.
- 🧑‍⚖️ **Abertos, sem implementar (permit consumido):** **F98** (guarda de blackout so ve intervalo >= 4d) · **F99** (nao ha CLI que sirva card por id) · **F100** (re-ensino nao fecha fato arbitrario) -- `AUDITORIA_MEDHUB.md §6v`. 🆕 **Candidato s180:** backfill do **override do modal** no ledger de habilidades (13 questoes do S9 via `habilidades.py --add --veredito errou --questao-id N`) -- hoje o padrao existe no playbook e na memoria, **nao no ledger**.
- 🔜 **ABERTURA DA JANELA 4 (decidida pelo `/ai-eng`):** o smell **`db.py -> tools/card_checks` por `__file__`** (camada invertida, toca 7 writers). Por spec: `gen-spec -> implement -> audit`, com §11 linha 1.15 como insumo.
- 🧑‍⚖️ **1.10 segue CANDIDATO, sem GO do operador.**
- 🧑‍⚖️ **Decisoes empilhadas do OPERADOR:** (a) `reforja.py --backfill --apply`; (b) RODADA 3 do `normalize_taxonomia` (18 linhas fantasma); (c) ⚰️ overflow 13-14/09 -- **decidido s179: para 15/09+, nunca antes**; (d) backfill UTC->local; (e) `--new-limit` x pool 676 -- **cabem ~460 ate 01/11 no teto de 60/dia**; (f) `Oncologia`/`Urologia`/`Radiologia`/`Medicina de Emergencia` sao areas?; (g) F64; (h) G1/G8 rotacao do ledger (~260 KB) = F62; (i) F57 lote de ESTUDO; (j) os de sempre: `/graphify`, F35, F87, F62/F55/F37.

## Estado por frente

- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (50d). ENAMED 13/09 (**amanha**) termometro.
- **Volume & Metas:** 7226 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~63.5q/dia. 🔴 **A grade NAO fecha a meta:** 1.927q restantes levam a ~9.150, ainda ~1.250 abaixo do marco.
- **Simulados:** 9 provas · **S6 80 · S7 82 · S8 82,1 · S9 86** -- quatro seguidas acima do banco. Serie: **239 erros = 60% execucao x 40% lacuna**. Gargalo novo: **override do modal** (13/13 no S9, custo 4-5q).
- **FSRS:** divida 14 atrasados + 64 p/ hoje -- pool 676 nunca introduzidos (entram <=90/dia). (+8 erros frescos). Calendario: ~55 em 15/09 (26 + ~29 do blackout), depois 7-16/dia (vacuo).
- **Conteudo:** 136 resumos. **327 temas com PDF e sem `.md`.** Polipos/Neoplasias e Farmacodermias sem lastro.
- **Erros & Cards:** 1016 erros registrados · 1432 cards ativos · 2 needs_qualitative na fila · taxonomia 294 temas. [derivado: db] Reforja: **272 abertas**.
- **Engenharia:** suite **621** · `auto_check --all` PASSED · ledger **102 ids**.
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem).
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario).

## Ultima sessao -- s180 (2026-09-11 noite -> 12/09) -- ESTUDO

Detalhe integral em `history/session_180.md`. Overview: `artifacts/raio-x-simulados.html` (artifact publicado).
🎯 **Simulado 9 = 86/100** (ENARE 2024; 5 anuladas, ele errou so a Q1; Q82 provisorio). Volume registrado ANTES da analise. Gabarito derivado do PDF pelo casamento "N% ACERTARAM" x % da alternativa (2a confirmacao do metodo).
🔴 **O fio: o override do modal.** Nas 13 erradas reais ele marcou a alternativa **nao-modal em 13/13** (media 17,9% x gabarito 63,5%; Q66: 2% x 88%). Em 4 ele **narrou** ter abandonado a que julgava certa. **Custo 4-5 questoes: o 86 era 90-91.** Familia NOVA -- a analise clinica termina certa e uma meta-decisao a descarta; **nao se corrige com conteudo**. O S8 ja mostrava (*"nunca o dominante"*) e ninguem nomeou. Portadores: playbook (sub-familia + item 7), memoria, campo de armadilha dos cards.
🃏 14 erros no banco (Q1 sem card), 13 cards -- **7 nasceram compostos por minha autoria**, linter acusou, **11 reforjados antes de entrar na fila**. `[SEM-LASTRO]` Polipos e Neoplasias Intestinais.
🩻 **Raio-X dos 9 simulados:** 239 erros, 60/40; mecanismo S2-S4 = 81% processo; **Clinica Medica 33% dos erros para 20% da UERJ**; MFC zero; tabela padrao -> tema -> remedio (9 linhas).

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- 🆕 **Override do modal:** n=13, uma prova; o S8 e precursor por leitura retroativa, nao por medicao. Vale como padrao **nomeado**, nao como lei -- o S10 mede de novo.
- **F98/F99/F100:** guarda de blackout nao ve intervalo < 4d · re-drill inter-sessao so funciona por acaso · F100 e n=3, 24h, um tema.
- **F7:** classe real, nao-verificavel por gate. **F39:** entrega onde registrar, nao o conserto.
- **D5** mede presenca, nao semantica · **G10** isenta por LINHA · **G5** sensivel a arquivo novo · **G14** ve rotulo · gate de revogacao casa substring literal.
- Herdadas e vivas: **F35** · **F89** · **F79b** · **F66** (34% de orfandade) · **F64** · eixo C do **F81** · sitios gemeos do **F80b**.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB: baixar uma vez resolve beta-hCG e cortes da PE.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial), SINAN 2026.
- ⚠️ Drive 47d sem sync (F72); Dashboard EMED x db medido pelo boot (F35).
- 📡 Canal com o `/ai-eng` em `history/exchange-log.jsonl`. Portador dele: `C:/Users/daanm/ai-eng/brain/interactions/2026-09-10-handoff-medhub-reforma-subagents.md`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_180.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
