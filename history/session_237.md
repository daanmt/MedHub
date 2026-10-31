# Sessão 237 -- 2026-10-30 (noite) (Opus 5.5)

**Data:** 2026-10-30 (22h30 -> 01h) · **Ferramenta:** Claude Code (Opus 5.5) + 17 subagentes Opus (6 gabarito do Sprint, 3 aulas, 2 análises + RD, 3 cunhagens de Solução v3, 3 correções)

Pedidos dele: (1) *"o estratégia med acabou de soltar um documento de sprint da uerj [...] '250 questões inéditas' [...] confio mais em você com a análise das provas antigas"*; (2) *"gerar outros dois materiais no bloco teoria: sprint uerj emed, e um dos meus erros até aqui nos simulados uerj, expandindo nos pontos prevalentes"*; (3) TB 360 feita (*"o buraco: tratamento de acordo com o contexto, além de confusões sobre o PPD"*); (4) t740 sem elos; (5) t740 feita, RD expandida ao diferencial (AIJ, epifisiólise, Perthes, osteomielite, tumores).

## O que foi feito
- **Sprint UERJ (PDF da Estratégia, 250 inéditas, sem gabarito):** a API do EMED não serve (só busca caderno; recusa questão sem banca, regra dele da s198). Gabarito autoral por 6 subagentes Opus (CM 1-47, 48-94, CIR, GO, PED, PREV): 208 alta / 34 média / 8 baixa; 33 com defeito; amostra cega do principal 9/9. Veredito medido: 20% das questões em tema de prevalência alta x 34% na própria UERJ 2021-2025; quase o dobro de CM. Insumos em scratchpad da sessão (`sprint/`); nada do texto deles no git.
- **Spoiler corrigido:** as aulas usavam `prevalencia_uerj.json` (2021-2026); trocado por contagem 2021-2025 (420 q) nas 3 aulas e na RD de TB.
- **Aulas no hub (Version 147, depois 148):** `erros-uerj-1` (CM+CIR, 66 erros), `erros-uerj-2` (GO+PED+MFC, 71 erros), `sprint-uerj` (veredito, top 30, gabarito comentado, divergências, grade), `rd-tb-3010`, `rd-orto-3010`; todas com `tarefas: [5426]` (cartão de 31/10). Lidas inteiras pelo principal antes do publish; UI conferida (`tmp/ui_capturas/s237*`).
- **TB 360 (t1797) = 11/20** -> `sessoes_bulk` 150, #1797 feita; 6 erros (#1307-#1312), 12 cards (2275-2286, quarentena do evidence-bank), 4 habilidades de desatenção, 12 análises no hub; Q6 = conflito aberto (todos os elos Sim e errou).
- **t740 = 5/11 (7 chutes)** -> `sessoes_bulk` 151, #740 feita; 4 erros, 11 cards, 6 habilidades, 10 análises; Q3 fora do lote (veio sem o caso clínico).
- **Cadeia v3 que faltava:** t740, t876, t878 (39 questões) cunhadas e gravadas no hub; `core/objetivos.json` ganhou "Oncologia ortopédica e osteomielite"; fontes "Apostila EMED"/"Resumo" retiradas da t876 (regra s236).
- Painel regenerado (8.193). Suíte 1835 no commit 55be47e.

## Para ele decidir (correções clínicas, antes -> depois + fonte)
Lista consolidada em `tmp/s237_divergencias.md`. Inclui: TARV na TB meníngea (MS 2019 8 sem x PCDT 2023 4-6 sem); BPaL x BPaLM (NI 1/2025); 3HP como ILTB preferencial; escore da criança aceita IGRA; osteomielite pediátrica VO guiada por PCR, 3-4 semanas (aulão cap. 10); EGB 36-37 sem (resumos dizem 35-37); VSR a partir de 28 sem (`Pré-Natal.md` l.201); aulão parte 2 atribui "12% e 200 mL" à ERS/ATS 2022 (é GINA); card do corpus EMED (não do nosso FSRS) diz não explorar zona I contusa.

## Pendente
UERJ 2026 (t890) não feito; Q6 da t1797 e Q3 da t740; varrer listas fora do sprint sem cadeia (`emed_banco.py --status` acusa SEM_CADEIA em ~20 listas antigas); como essas 3 listas foram ao hub sem cadeia (`--sem-cadeia`?) é pergunta para o ai-eng.

## Fechamento (31/10, ~00h20)
- Tique: lote `2026-10-31a` sem notas; quadro com 4 assinaturas novas (rd-cir-2910, rd-go-2910, rd-mfc-2910, topicos-pediatria); Painel de 31/10; hub **Version 149**, `--confirmar` OK.
- Pendências amarradas no item 0 do HANDOFF.
