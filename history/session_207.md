# Session 207 -- Decisões do operador aplicadas (M1-M5, M7, M11) + micro-lote de engenharia + regime do ledger

**Data:** 2026-09-29 (terça, 20h-23h45) - **Ferramenta:** Claude Code (Opus 5.5) - **Continuidade:** `session_206.md`

---

## Pedido do operador

A sessão abriu com o /ai-eng pedindo o estado (canal reaberto). O operador respondeu as decisões da folha na sessão do /ai-eng e, no chat desta sessão, confirmou: *"aprovados, pode seguir"* (as 8 decisões, a limpeza das órfãs e a opção A para as 33). Depois ratificou por pergunta fechada: #359, #1307 e #205 mantidos; M3 = "As 11"; M4 = "Aprovo todos".

## O que foi feito

1. **Hotfix `db.fechar_reforja` (`62b049b`):** o motivo gravado passa a ser o normalizado; desfecho de par sem marca aberta levanta `SemMarcaAberta` e não grava. **Limpeza das órfãs com aprovação dele:** `reforja_marks` 988 -> 930 (G1 = 25 `X\r` da s206; G2 = 33 `reforjado s205`), COUNT-ASSERT separado, abertas 24 = 24, backup fixado `ipub_fixado_20260929_205330` (sha256 62719982...). O 1º DELETE foi barrado pelo classificador e só rodou depois do "aprovados" dele no chat.
2. **M11 (9 cards de evidência):** banca + alerta em #760 #777 #358 #1113; banca-dependentes #1172 #1176 #65; #21 ensina V/Q com nota "EMED diz absorção". Incertos: #659 MANTER (RBEHG 2025: neuroproteção 23-32 semanas); #205 posologia corrigida (dias alternados, MS). #780 segue retido no lote vivo 30a.
3. **M2 (faixa 600-800):** 290 cards, 4 reforjadores Opus, validador com `--frente-travada` (frente idêntica ao banco). Só o verso encurtou, 0 extras; depois: 0 cards >= 600. Lentes: fatos/removido, polaridade, pt_sensor e amostra de 8 a olho. O principal corrigiu #1307 (CF art. 199: o lucro não é vedado) e pôs em #359 o alerta do #358. 🔴 **Os três (#359, #1307, #205) saíram fora do que ele tinha decidido:** o /ai-eng apontou e o operador RATIFICOU os três por pergunta fechada. 90 frentes com defeito ficaram anotadas em `tmp/varredura_s206/m2_notas_frente_e_duvidas.json`, como oferta a ele.
4. **Micro-lote (`a1b32e7`):**
   - **F141:** `app/utils/relogio.dia_logico`, função única no adapter e na entrada do Optimizer. Golden de partida: 1.248 divergências, todas onde calendário != 24 h. Refit antes/depois no histórico.
   - **F142:** MESMO_DIA vai para a quarentena; teto por card distinto.
   - **F127:** `--corrigir`.
   - **F122:** re-medido e confirmado; 741 tarefas.
   - **O-2:** py-fsrs 6.3.2 muda 12 linhas, todas mesmo-dia + Hard.
   - **F128:** condição dividida -> LIMITE; os 5 overrides estão anotados.
5. **Regime de saldo mínimo (`f2765ef`):** 3º destino `history/auditoria/limites_conhecidos.md` (terminal LIMITE com `revisar:`, acusado ao vencer) + `vizinhos:` obrigatório em achado novo (> F142). M5: F68 SUPERADO. M7: F87 LIMITE.
6. **M3 / F67 (`adce128`):** 11 fusões (8 de 09/09 + 3 novas mostradas a ele), 320 -> 309 temas. A fusão passou a re-apontar `review_log` e `questao_habilidades`, que ficariam órfãs.
7. **M4 / F65 (`9f20f5e`):** os 35 cards de `[bulk]` foram para o tema real (`MOVE_CARD`), 0 cards ativos em `[bulk]`. Os 201 erros em `[bulk]` seguem GATE dele.
8. **Legado do STATE do /ai-eng:**
   - Resolvidos: `--new-limit` x pool (F140), F37 coluna erros, contexto obrigatório em card novo (gate de dêixis F79b), `--mover` x `plano_custom` (F120), terminal da reserva (`plano.py --reserva`), G1/G8 (declarados em `docs/MEMORIA-AUDITORIA.md`).
   - 17 cards do overflow: a mecânica existe (`db.overflow_blackout`); a conferência dos 17 específicos está pendente.
   - LIMITE (revisar 02/11): F143 backfill UTC -> local e F144 meta de retenção 0,90.
9. **Plano re-semeado:** +6 tarefas da S48 (F122), 0 mudanças nas 903 existentes.

**Selo:** frente 19 -> 11; 4 limites conhecidos. Suíte 1277.

## Tropeços

- Heredoc do bash quebrou com aspas triplas e com `\b` (virou backspace no regex). Remédio: patch longo em arquivo do scratchpad (lição já registrada na memória).
- O `sed` de uma linha da tabela 7.4 do AGENTE.md pegou 3 linhas; a regeneração pelo gerador corrigiu.
- Mudança clínica fora da decisão (#359, #1307, #205). O /ai-eng pegou e o operador ratificou. Lição: correção de conteúdo encontrada durante um lote de FORMA é mostrada a ele (antes -> depois, fonte) antes de aplicar.

## Próximo

Ver o "ABRIR A s208" do `HANDOFF.md`.
