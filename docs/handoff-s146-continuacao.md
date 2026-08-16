---
type: handoff
layer: root
status: active
---

# Continuação da sessão 146 — o que ficou pendente

> Escrito ao fim da s146 por esgotamento de janela de contexto. Retomar por aqui.

## Contexto da virada

O usuário corrigiu uma premissa minha: **ENARE == ENAMED** (a nota do ENAMED é usada no ENARE;
ENAMED está para o ENEM assim como ENARE está para o SiSU). Logo o Guia Estatístico do ENARE
**é** a fonte boa de prevalência. Minha camada "blueprint ENAMED medido" era ruído: os 120 erros
são os erros DELE (enviesados pelas fraquezas dele) e o Simulado 2 é um simulado do EMED, não a
prova. A fila foi refeita só com o guia.

## O que JÁ FOI FEITO e está aplicado

- **Acentuação do `ipub.db`**: 119 dos 120 registros de erro dos simulados tiveram acentos
  restaurados. Método: dicionário de 2.035 palavras colhido dos próprios
  `resumos/**/*.md` (`core/simulados/acentos_pt_br.json`) + passe de sonnets sob invariante dura
  `sem_diacriticos(novo) == sem_diacriticos(antigo)`, verificada por `tools/aplica_acentos.py`.
  1 registro (#808) foi REJEITADO pela invariante — o agente mudou além do acento.
- **Comandos das questões**: 53 gravados no `enunciado` (39 verbatim do PDF do Simulado 2, 14
  inferidos das alternativas nas questões do S4). Procedência em
  `core/simulados/comandos_recuperados.json`. Agora **120/120 erros têm comando**.
- **Artefato Autópsia republicado** (mesma URL): bloco "O discriminador que faltou" no lugar da
  repetição do texto longo do mecanismo; prosa justificada com hifenização; botão
  compactar/expandir por bloco (187 no total); filtros minimalistas com as 5 grandes áreas
  (cirúrgicas incluem ortopedia/otorrino/oftalmo) + subespecialidades; busca virou campo pequeno
  com lupa; **todas as 120 questões usam o mesmo desenho de alternativas** (S3/S4 mostram só o par
  registrado, marcados como parciais).
- **Fila recalculada só com o guia**: `core/simulados/fila_enamed_payload.json` já atualizado
  (16 blocos puxar / 15 empurrar). `Estatística Médica` (6 slots) passou a ENTRAR na janela —
  era o que a camada macro errada suprimia.

## O que FALTA (retomar aqui)

### 1. Reforja dos 138 cards -- CONCLUIDA

131 cards reforjados in-place + 7 aposentados, via `tools/recurate_cards.py --apply`
(card_id e estado FSRS preservados, card_version incrementado). Os 4 gates aprovaram os 138
itens. Defeitos de formulacao no baralho inteiro: **138 -> 9**.

Os 14 que o gate barrou na primeira passada eram quase todos pergunta com dois nucleos
("X **e** Y") -- reescritos a mao para um criterio de acerto cada. Licao para o proximo lote:
por no prompt do agente que a pergunta nao pode ter conjuncao ligando dois pedidos.

Sobraram **9 cards** com defeito, fora da worklist original -- varrer com `card_checks` numa
proxima passada.

### 2. Artefato da fila com o modelo guia-only

`core/simulados/fila_enamed_payload.json` já está com os números certos, mas
`tools/fila_enamed.py` ainda tem o TEXTO da versão anterior (fala em "blueprint ENAMED medido",
"o cronograma está calibrado para outra prova"). **Reescrever a narrativa**: a tese agora é
ROI por slot com o guia como verdade, não descalibragem de blueprint. Depois republicar em
https://claude.ai/code/artifact/8a3fcf35-a82c-471f-a2d4-9bc89a5c28e8

### 3. Acentos -- CONCLUIDO (119/120)

Todos os 6 lotes entraram. Restou **apenas o #808**, rejeitado pela invariante -- reprocessar a
mao. Diagnostico intermediario que eu registrei aqui ("os agentes reescreveram conteudo") estava
ERRADO: a causa real era o primeiro arquivo do lote 2 vir com escape de HTML; o agente regravou e
passou limpo. Nenhum conteudo reescrito entrou no banco em momento algum.

`tools/aplica_acentos.py` tolera o sufixo do comando anexado ao `enunciado` (o comando foi gravado
DEPOIS que os agentes leram o texto).

### 4. Cards que o artefato mostra

Depois da reforja, **regerar e republicar a Autópsia** (`python tools/autopsia_simulados.py`)
para que os cards exibidos sejam os reforjados.

## Backup

`artifacts/backups/ipub_backup_20260816_163256.db` foi tirado antes de qualquer escrita.
