---
type: session
---

# Sessão 082 -- Revisão de Cardiopatias Congênitas + evolução "cards de altura graduada"

*2026-06-14 | Claude Code (Opus 4.8)*

## Resumo

Sessão híbrida: revisão + engenharia de método. Abertura com revisão (`/revisar`) sobre o cluster de Cardiopatias Congênitas -- os 12 cards "travados" herdados do HANDOFF da s081. O drill expôs que o problema **não era falta de material** (o resumo `Cardiopatias Congênitas.md` existe e é gold) nem cards mal escritos, mas **falta de grounding do estudante** num tema frio. Disso nasceu -- co-desenhada com o usuário -- a evolução **"cards de altura graduada"**.

## Revisão (12 cards-alvo de Cardiopatias Congênitas)

- Boot/reconcile limpo (0 BLOCKING). **Correção factual:** HANDOFF/ESTADO da s081 registravam Cardiopatia como "tema zero a criar" -- falso; o resumo é gold e completo, e 10 dos 12 cards eram **estreias** (state 0), não "travados". Só c90/c94 tinham sido vistos e falhados.
- Refresh pré-bloco dirigido + 3 lotes (c90/95/97/102 · c94/96/98/100 · c104/106/108/110). Distribuição honesta: poucos 4, vários 1-2. **HCE** ("nem lembro o que é") foi o buraco; **c108** identificado como tangencial (transporte, não cardiopatia) -> marcado p/ recontextualização.
- Padrão fino diagnosticado: o gap é **causalidade/mecanismo, não fato** -- o usuário tem as peças, mas não monta a cadeia.

## Evolução de método -- cards de altura graduada

- **Tese (do usuário, refinada em conjunto):** a altura de um card é um **gradiente** `base -> mecanismo -> nuance -> topo`, não um par base/alvo. Andaime de pré-requisito reconstrói os elos a montante quando um **cluster** trava por grounding. **Propagação local:** costurar o degrau adjacente ao buraco; nº de degraus inferido da iteração. Compressão calibrada ao nível do estudante (refresh pré-bloco).
- **Consultado `C:\Users\daanm\ai-eng`** (subagente Explore): grounding, subcategory targeting, tiers de autonomia (schema change = Tier 3), velocidade > perfeição.
- **Construído (Tier 1, sem schema change):**
  - `tools/insert_card_base.py` -- insere cards de andaime (`questao_id=NULL`, altura no campo `tipo`), idempotente, `--dry-run`.
  - **8 cards de andaime** no tema 121: 5 `base` (ids 438-442) + 3 `mecanismo` (ids 443-445), tapando os buracos do re-teste (c94/c96/c100).
  - Tese provada em parte: na altitude da base o usuário foi muito melhor (438->4) que nos alvos -- conhecimento **inacessível, não ausente**. A transferência base->topo não é de uma sessão (FSRS ao longo dos dias).
- **Documentado:** `estilo-flashcard.md` (§Altura graduada + assinatura do CLI), `revisar.md` (Camada 0 -- refresh + compressão calibrada), `AGENTE.md` (§6 decisão + §7.4 CLI), memória `cards-altura-graduada`.

## Decisões

- Altura de card = gradiente no campo `tipo` (`base`/`mecanismo`/`nuance`/topo). Sem schema change (Tier 1).
- **Tier-3 pendente (espera OK):** schema formal de altura (ordinal + grafo `prereq_de` + fila auto-ordenada base->topo).
- 3ª categoria de diagnóstico de card: **card-bom-órfão-de-base** (além de card-ruim × tema-não-dominado).

## Próximo

- **VOLUME (questões)** -- 2 sessões a 0; é o gargalo. Refresh pré-bloco antes do bloco da área.
- Drillar a escada de cardiopatia via FSRS (HCE volta amanhã). Re-testar os 4 refeitos da s081 (428/68/74/82).
- Aplicar altura graduada a outros temas frios (Hemato, LRA). Decidir Tier-3.

*0 questões (sessão de revisão + engenharia de método).*
