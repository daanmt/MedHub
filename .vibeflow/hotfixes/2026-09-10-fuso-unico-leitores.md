# Hotfix: fuso-unico-leitores

origin: session
status: verified

## Symptom

Medido em 2026-09-10 20:50 local (BRT, UTC-3), com o comando na mao:

```
sqlite> select datetime('now');              -> 2026-09-10 23:50:41   (UTC)
sqlite> select datetime('now','localtime');  -> 2026-09-10 20:50:41
python> db.agora()                           -> 2026-09-10 20:50:41
delta UTC - local                            -> +3.0 h
```

Os writers do `ipub.db` gravam em hora LOCAL naive -- e o contrato F80
(`app/utils/db.py:43`, `db.agora()` = "o relogio unico do ipub.db"), fixado pela
suite `tools/test_fuso_unico.py`. Mas tres SELECTs de producao em
`app/utils/db.py` comparam essas colunas locais contra o `'now'` do SQLite, que
e UTC. Efeitos observaveis:

- `get_fresh_error_cards` (`:216`) e a banda `erros_frescos` de
  `get_cards_by_bucket` (`:928`): `fc.due >= datetime('now', '-48 hours')`. Como
  `'now'` esta 3h adiante do relogio que gravou o `due`, o corte real cai em
  `local - 45h`: **a janela de 48h opera como 45h** e o card de erro fresco sai
  da banda prioritaria 3h antes da hora.
- `media_diaria` (`:191`): `data_sessao >= date('now', '-N day')`. Entre ~21h e
  meia-noite locais o `date('now')` **ja e o dia seguinte** em UTC, e a janela de
  volume desliza um dia inteiro.

🔴 A assimetria e o que torna o defeito invisivel: na MESMA funcao
`get_cards_by_bucket`, os buckets `atrasados` e `hoje` ja usam relogio local
(`now = datetime.now()`, `:892-894`) -- foi o que o F80 consertou do lado do
leitor. A banda `erros_frescos`, adicionada depois (P3 part-2), ficou para tras.
Duas bandas da mesma fila respondem a dois relogios diferentes.

## Checkpoint

hypothesis: os leitores nao tem um ponto unico de "agora". Quem foi escrito
depois do F80 pega o relogio do SQLite (UTC) porque e o que esta a mao dentro do
SQL, enquanto os writers ja passam por `db.agora()` (local). O consumidor nao
tem como notar: o retorno e uma lista plausivel, so que menor.

falsification_test: congelar `db.agora()` num instante e posicionar cards
relativos a ESSE instante. Se o leitor obedecesse ao relogio unico, o resultado
seria funcao apenas do instante congelado. Se ele ignora `db.agora()`, o
resultado passa a depender da hora real da maquina -- e com o instante congelado
no passado, a janela de 48h contada a partir do "agora" real nao alcanca nenhum
card e o retorno vem vazio.

blind_spots: (a) o teste projetado nao mede o offset de 3h -- mede *obediencia ao
relogio unico*, que e a propriedade contratual; um CI em UTC teria offset 0 e um
teste ancorado em "3h" passaria por acidente; (b) o backfill do historico ja
gravado em UTC NAO e tocado aqui (Tier 2, item 2.3, decisao do operador); (c) o
`DEFAULT CURRENT_TIMESTAMP` do schema e outro eixo, ja documentado em
`app/utils/db.py:17-20`.

## Preservation

- `get_cards_by_bucket` continua devolvendo os quatro buckets com a mesma ordem
  de servico e o mesmo `selection_reason` por card -- muda o CORTE, nunca a forma.
- Nenhum write: `stability`, `difficulty`, `due` e o agendamento FSRS ficam
  intocados. Este hotfix so le.
- `tools/test_fuso_unico.py` (writers, F80) segue verde -- o relogio unico ganha
  leitores, nao muda de definicao.

## Root cause

Nao ha um leitor unico de "agora" do lado do SELECT. `db.agora()` foi
estabelecido como relogio unico para WRITERS (F80) e a suite que o protege
(`test_fuso_unico.py`) varre INSERTs. Nenhum gate olhava para o lado da leitura,
entao cada SELECT novo escolheu sozinho -- e dentro do SQL a escolha obvia
(`datetime('now')`) e justamente a errada, porque o SQLite responde em UTC.

E a mesma classe do F80, um lado adiante: **o relogio unico existia e nao
alcancava metade das superficies**. Reachability-Debt, variante "sem cobertura de
gate": a regra estava certa, o gate media so os writers.

## Fix

files_changed: `app/utils/db.py` (1 arquivo de codigo; + `tools/test_fuso_unico_leitores.py` e `pytest.ini`, que nao contam no teto)

Os tres SELECTs deixam de perguntar a hora ao SQLite e passam a receber o corte
ja calculado a partir de `agora()`, chamado pelo atributo do modulo (o que a
docstring do proprio `agora()` declara ser o ponto de monkeypatch):

- `get_ritmo_real` (o `media_diaria` do Symptom -- nome que eu havia assumido;
  ver Deviations): corte = `agora().date() - timedelta(days=janela_dias)`,
  passado como parametro; o SQL vira `data_sessao >= ?`.
- `get_fresh_error_cards`: corte = `agora() - timedelta(hours=janela_horas)`,
  formatado com `FORMATO_CARIMBO`; o SQL vira `fc.due >= ?`.
- `get_cards_by_bucket`: `now = datetime.now()` vira `now = agora()` (a funcao
  inteira passa a ter UM relogio, em vez de dois), e a banda `erros_frescos`
  recebe o corte derivado desse mesmo `now`.

O relogio unico deixa de ser convencao e vira **assinatura**: quem le passa o
instante, quem consulta nao pergunta as horas.

## DoD

- [x] Com `db.agora()` congelado, os tres leitores devolvem resultado funcao
      APENAS do instante congelado -- zero dependencia do relogio da maquina.
- [x] A varredura estrutural falha nomeando `arquivo:linha` quando um SELECT de
      producao em `app/` usa `datetime('now')`/`date('now')` sem `'localtime'`.
- [x] `tools/test_fuso_unico.py` (writers) continua verde -- nenhuma regressao no
      contrato F80.
- [x] Suite completa verde e `auto_check --changed` PASSED.

## Regression

WHEN `db.agora()` esta congelado em `2026-09-07 21:30` e existem cards de erro
com `due` em `2026-09-07 20:00` (1,5 h antes) e `2026-09-05 22:00` (47,5 h antes,
dentro da janela de 48 h) e `2026-09-05 12:00` (57,5 h antes, fora)
THEN `get_fresh_error_cards()` devolve exatamente os dois primeiros.
Sob o codigo defeituoso devolve **zero**: o corte e contado a partir da hora real
da maquina, que esta dias a frente do instante congelado -- o que prova que o
leitor ignora o relogio unico, sem o teste depender do offset da zona.

test: `tools/test_fuso_unico_leitores.py`
oracle_type: specified
reproduction: real
verification: red-green

## Deviations

- **Escopo estreitado ao `app/`, deliberadamente.** A varredura encontrou mais
  tres sitios do mesmo defeito FORA de `app/`: `tools/audit_fsrs.py:38,39,44`
  (`datetime('now','start of day')` para contar due-hoje/atrasados -- o "inicio do
  dia" e UTC, o corte cai as 21h locais do dia anterior) e `tools/variancia.py:194`
  (`data_sessao >= date('now', ?)`, mesma janela deslizante do `media_diaria`).
  Corrigi-los aqui levaria o hotfix a **3 arquivos de codigo**, acima do teto de 2
  -- e a regra do teto existe justamente para impedir que um hotfix vire
  refatoracao. Ficam DEFERIDOS para uma chamada propria (2 arquivos, dentro do
  teto), e a varredura declara o proprio escopo na docstring em vez de fingir
  cobertura total: sensor que nao cobre por desenho e declarado, nunca verde por
  omissao (`AGENTE.md §10.8`, corolario verification-stack; e a licao do D11).
- **Colateral nao relacionado, deferido:** `tools/insert_questao.py:263` faz
  `UPDATE cronograma_progresso SET updated_at = CURRENT_TIMESTAMP` -- um WRITER em
  UTC que a varredura de INSERT do F80 (`test_fuso_unico.py`) nao pega porque so
  olha `INSERT INTO`. Eixo do F80, nao deste hotfix. Registrado para nao se perder.
- **A varredura acusou a propria prosa.** Na 1a rodada ela marcou `app/utils/db.py:189` e `:213`
  -- os COMENTARIOS que eu acabara de escrever explicando o defeito. Corrigido cortando a linha no
  primeiro `#` antes de casar: comentario que NARRA o defeito nao e o defeito. E literalmente a
  mesma distincao que o gate `CONTRATO_REVOGADO` faz entre lapide e prescricao ativa -- dois gates
  independentes chegando na mesma regra. Limite aceito e nao mascarado: um `#` dentro de string SQL
  truncaria a linha e esconderia um sitio; nao existe nenhum hoje.
- Dois erros meus de autoria do teste, corrigidos contra o schema real: a coluna e
  `questoes_acertadas` (nao `acertos`) e o leitor de volume chama-se `get_ritmo_real` (nao
  `media_diaria`, nome que eu havia assumido do enunciado do achado). Ambos pegos pelo proprio
  teste, antes do fix -- que e para isso que o vermelho serve.

## Verificacao final

- regressao: **6 testes, 6 vermelhos antes do fix -> 6 verdes depois**. A varredura estrutural
  nomeou exatamente os 3 sitios previstos (`db.py:191`, `:216`, `:928`) no vermelho.
- suite detectada: `pytest tools/ -q` -> **458 passed** (baseline 452 + 6 novos), zero falhas
  pre-existentes.
- Critical Gate: limpo -- o diff so troca expressao de corte em SELECT (read-only), adiciona um
  arquivo de teste e registra a suite no `pytest.ini`. Zero escrita nova no banco, zero DDL, zero
  operacao destrutiva.
