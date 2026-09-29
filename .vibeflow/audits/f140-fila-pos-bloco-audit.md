# Audit Report: F140 -- fila pós-bloco re-serve no mesmo dia cards recém-errados

**Data:** 2026-09-28 (s204) · **HEAD base:** `bb6e62e` · **Objeto:** entrada F140 de `AUDITORIA_MEDHUB.md`, escrita na s203 pós-selo

**Veredito do documento auditado: PARTIAL** -- os fatos observados estão certos (4 de 9 afirmações confirmadas), a **causa está errada** e o achado **não era novo** (reincidência do F32).

> **Razão declarada para o formato:** auditoria de um documento de ledger, sem spec em `.vibeflow/specs/`.
> O DoD é o do plano da auditoria (`tmp/f140_auditoria/PLANO-AUDITORIA.md`). Anti-escopo: nenhuma linha de
> `app/`, `tools/`, `core/` mudou; `ipub.db` real intocado (leituras em `mode=ro` e sobre cópia).

## Método

| Lente | Quem | O que fez |
|---|---|---|
| Medição direta | principal | 11 cards no banco, lotes `28a`/`28b`, fonte do py-fsrs instalado, escala no revlog |
| O1 | filho Opus | replay no py-fsrs, escala, simulação dos remédios sobre cópia do banco |
| S1 | filho Sonnet | alcance no código: consumidores do estado 3, teto, testes que prendem |
| S2 | filho Sonnet | portadores de norma: contratos, skills, ledger, fundamentos, git |
| O2 | filho Opus | evidência externa (web isolada): Anki, py-fsrs, FSRS, literatura |

Números de escala só entraram depois de duas lentes independentes baterem (principal x O1).

## DoD Checklist

- [x] **1. Veredito por afirmação** -- tabela abaixo, 9 de 9.
- [x] **2. Assimetria reproduzida** -- replay 11/11; controle: o revlog inteiro da era py-fsrs reproduz em 3.579/3.579.
- [x] **3. Escala medida** -- duas lentes, mesmos números (seção Escala).
- [x] **4. Remédios simulados** -- baseline reproduz o lote `28b` exato (ids, buckets, ordem).
- [x] **5. Duas lentes + amostra a olho** -- 5 citações do S1 e 6 do S2 conferidas no arquivo.
- [x] **6. Anti-escopo** -- `git status` só mostra os arquivos de documentação desta sessão.
- [x] **7. Ledger corrigido com lápide + report ao /ai-eng** -- F140 reescrito preservando o texto original; F141 e F142 abertos.

## Veredito por afirmação

| # | Afirmação do F140 | Veredito | Evidência |
|---|---|---|---|
| C1 | 11 notas < 4; os 5 defeitos "saem do FSRS" | IMPRECISO | notas < 4 = 15; notas < 3 (limiar da régua v2) = 12. O `1481` tem defeito E nota 1 gravada (revlog 3582, `state=3`) |
| C2 | lote `28b` = 3 re-serviço + 10 novos | CONFIRMADO | `tmp/player_2026-09-28b.json`; reprodução exata |
| C3 | assimetria "não explicada" | EXPLICADO | decide o par estado Review x nota Again; estabilidade é irrelevante (`1444` tinha S=15,9 e voltou; `640`/`644` com S=0,143 não) |
| C4 | causa = `learning_steps=()` + estabilidade baixa; intervalo pode ser < 1 dia | **REFUTADO** | `_next_interval` tem piso de 1 dia; a causa é `relearning_steps` no default (1 passo de 600 s); `learning_steps=()` é o que fez os 6 novos NÃO voltarem |
| C5 | bucket `hoje` = `due` no dia, sem marca de recência | CONFIRMADO | `app/utils/db.py:1176-1178` |
| C6 | ordem fixa de buckets | CONFIRMADO | `tools/fsrs_queue.py:108`; a docstring da linha 20 lista 3 buckets, a função usa 4 |
| C7 | `--new-limit` 10 capa os novos | CONFIRMADO | `tools/fsrs_queue.py:583`; o lote cortou pelo pool (13), não pelo saldo (53) |
| C8 | "uma causa, dois sintomas" | REFUTADO na causa | o gatilho comum é o passo de 10 min + `hoje` por `due` |
| C9 | mexer no Again "quebra a fidelidade ao FSRS" | REFUTADO | `relearning_steps` é parâmetro de agendamento; a biblioteca tem ramo próprio para `()`; S e D saem idênticos (4/4) |

## O que o documento omitiu

1. **É reincidência do F32** (`AUDITORIA_MEDHUB.md:390`): mesmo mecanismo, causa certa, medido na s112 e re-triado na s176. O F140 não o cita. A recomendação do F32 (documentar no `revisar.md`) nunca foi cumprida.
2. **O comportamento está em contrato:** `revisao-calibrada-contract.md:232` (Cláusula 14) -- nota 1 = "único lapso; o card volta hoje". Não é bug de código; mudar é decisão de produto.
3. **Manter o passo nunca foi decisão pedagógica:** commit `46df800` (03/06), justificativa "preserva o estado Relearning (3)". Contradiz `PLANEJAMENTO-APRENDIZAGEM-2026-09-17.md:93` (relearning intra-sessão é "do agente/player, não do motor").
4. **Relearning duplo:** o player já re-drilla nota < 3 dentro do lote sem gravar; o passo de 10 min re-serve os mesmos cards no lote seguinte e GRAVA a 2ª nota. Mesmo padrão em 27/09 (lote `27b`: 4 de 10).
5. **Loop:** em Relearning, nota 1 dá +10 min e nota 2 dá +15 min; só 3 ou 4 saem.

## Escala (revlog inteiro, 3.589 linhas, fuso corrigido)

| Medida | Valor |
|---|---|
| Revisões que terminaram em estado 3 | 362, desde 04/06/2026 |
| Depois do estado 3: 2ª nota gravada no mesmo dia | 49 |
| Depois do estado 3: amanheceu `atrasado` | 306 |
| Re-revisões no mesmo dia (todas descontam do teto) | 83; pior dia 08/08 = 27,8% |
| Revisões no ramo de curto prazo da biblioteca | 295; 212 em outro dia-calendário |
| Revisões servidas antes do `due` | 512 de 2.629 (19,5%) |

⚰️ Os números parciais que reportei antes da correção de fuso (65, 145, 150, 412) estão **superados** por estes.

## Remédios simulados sobre o estado real de 28/09

| Remédio | Lote resultante | Tira o re-serviço | Tira o "vira atrasado" | Custo |
|---|---|---|---|---|
| A: `relearning_steps=()` | 10 novos | sim | sim | 1 teste (`test_fsrs.py:73`), 4 portadores, `fsrs_optimize.py:318` junto |
| B: `hoje` exclui revisto no dia | 10 novos | sim | não | fixture de 7 testes sem `last_review`; espelhar em `db.bucket_de` |
| C1: `new_limit` = saldo | 53 novos | sim (corta) | não | ~+17 revisões no dia seguinte |
| C2: `new_limit` = saldo - vencidos | 50 novos + 3 no fim | não | não | idem |

Sob A não há migração: os 7 cards hoje em estado 3 voltam a Review na próxima nota, qualquer que seja.

**Evidência externa (O2):** pesa a favor de A com força moderada; contra B com força moderada; não decide C.
**Fundamentos do projeto (S2):** `FUNDAMENTOS-APRENDIZAGEM.md:59` e P10 (linha 121) pesam a favor de A.

## Achados novos (fora do F140)

| Id | Achado | Classe proposta |
|---|---|---|
| F141 | Card de 1 dia servido na manhã seguinte (< 24 h) cai no ramo de curto prazo: 212 revisões, 138 só em setembro. Contrafactual de modelo: nota 3 grava S=0,80 contra 2,58 no `due` | `spec` |
| F142 | Não existe trava de 2ª gravação do mesmo card no mesmo dia entre lotes; o teto conta linha, não card. 34 re-revisões vieram de card com `due` no futuro (lotes sobrepostos de 25/09) | `spec` |
| O-1 | Régua v2: nota 4 = 379 de 522 (72,6%); o contrato a descreve como "rara por construção" | conversa com o operador |
| O-2 | py-fsrs instalado 6.3.1; a 6.3.2 existe e corrigiria a queda de estabilidade com Hard no mesmo dia (uma fonte só, O2) | `spec` pequena, com golden de partida |
| O-3 | Deriva de documentação: 3 portadores listam 3 buckets, o código usa 4; `fsrs.py:46-48` diz "sem passos curtos" e mantém um | esforço S, junto do remédio |

## Limites declarados

- Valor pedagógico do passo de 10 min contra o re-drill do player: **não medido** (as tentativas do re-drill não existem no banco).
- O contrafactual do F141 é só do modelo; não mede o que ele responderia no `due`.
- Nenhum teste foi rodado sob os remédios; os testes afetados foram achados por leitura.
- O-2 tem uma fonte só; o changelog não foi conferido por segunda lente.
- As 19 re-revisões `futuro` de 08/08 não foram atribuídas a um caminho.

## Custo (lido do `usage` do harness)

| Filho | Tokens | Chamadas | Minutos |
|---|---|---|---|
| O1 Opus | 233.437 | 54 | 15,4 |
| S2 Sonnet | 220.508 | 74 | 9,9 |
| S1 Sonnet | 169.222 | 55 | 8,5 |
| O2 Opus | 124.610 | 40 | 7,0 |
| **Total** | **747.777** | **223** | 15,4 de parede |
