---
description: "Ingere o volume de questões das planilhas do Google (via Google Drive MCP) para sessoes_bulk, substituindo a extração manual de xlsx. O agente lê e mapeia; tools/importar_sessoes.py persiste."
type: skill
layer: commands
status: canonical
---

# Skill: Importar Planilha

Ingere o volume de questões a partir de uma planilha do Google (Sheets/xlsx no Drive) para a tabela `sessoes_bulk` do `ipub.db`. Coerente com a tese agent-first: **o agente lê e interpreta a planilha via MCP; o código (`tools/importar_sessoes.py` → `registrar_sessao_bulk.registrar`) persiste**.

Use quando o usuário pedir: "importa minha planilha", "puxa as questões do Drive", "atualiza o volume a partir da planilha do EMED", "verifica minhas planilhas".

---

## Pré-requisito: Google Drive MCP

Não existe MCP oficial do Google específico para Sheets — o acesso é via o connector oficial **claude.ai Google Drive** (tools `mcp__claude_ai_Google_Drive__*`), que lê Google Sheets como arquivos do Drive (export CSV/tabela). **OAuth já vinculado em 2026-06-03**; as tools aparecem após restart do Claude Code. Se algum dia desautenticar:

> Rode `/mcp` e selecione **"claude.ai Google Drive"** para reautenticar.

(O caminho de persistência local funciona independentemente do MCP.)

---

## Planilhas canônicas (registro)

As planilhas do Drive são a **fonte primária dos dados de performance e desempenho**, e uma delas é o **cronograma**. Registrado na primeira sessão com acesso (2026-06-03, sessão 075):

| Papel | Nome no Drive | ID | Destino no `ipub.db` |
|---|---|---|---|
| Volume/desempenho (questões por sessão) | `Dashboard EMED 2026` (Google Sheets nativo) | `1SCgQMK31WkaRzhjrCXTM04Zc2FuSG9IrTCCQwAoAxaA` | `sessoes_bulk` (via `importar_sessoes.py`) |
| Cronograma de estudos | `Cronograma de Reta Final.xlsx` (xlsx no Drive) | `157JEKQA9O49JxQHApOutKrVn7jW8JdIY` | conciliação com `taxonomia_cronograma` (leitura; persistência a definir) |

### Estrutura mapeada — Dashboard EMED 2026

`read_file_content` retorna o spreadsheet inteiro como tabelas markdown concatenadas, **sem os nomes das abas**. Ordem observada:

1. Tabela mensal: `Mês | Investimento | Questões | Meta | Custo/Q` (questões = acumulado no fim do mês).
2. Quadro Geral: `Disciplina | Tarefas Feitas | % Tarefas Feitas | Questões Feitas | % Acertos` (20 disciplinas). ⚠️ Pode divergir das abas por bug de fórmula (visto em Obstetrícia); **as abas por disciplina são a fonte autoritativa**.
3. 20 tabelas de tarefas (`Tarefa | Assunto | Tipo de Tarefa | Realizada? | Questões Feitas | Acertos | % Acertos`), uma por disciplina, nesta ordem: Pediatria, Preventiva, Cirurgia, Infecto, Obstetrícia, Ginecologia, Gastro, Endocrino, Cardiologia, Psiquiatria, Neuro, Nefrologia, Hemato, Pneumo, Dermato, Reumato, Hepato, Otorrino, Ortopedia, Oftalmo. ⚠️ A ordem **não** segue o Quadro Geral — confirmar cada tabela pelo conteúdo (assuntos) e validar a soma contra o Quadro Geral.
4. Tabelas `Disciplina | Questões Feitas | Acertos | % Acertos` adicionais (seções de acompanhamento, zeradas em 2026-06-03 — ignorar até ganharem dados).

Normalização de rótulos planilha → `AREAS_VALIDAS`: `Neuro`→`Neurologia`; demais coincidem. A planilha guarda **acumulados por tarefa**, não sessões — o delta a importar é `(total na aba) − (total em sessoes_bulk)` por área.

Regras:
- **Verificação:** quando o usuário pedir para "verificar as planilhas", ler via MCP e conciliar com o estado do `ipub.db` (`sessoes_bulk` via `/performance`, cronograma via `taxonomia_cronograma`), reportando divergências — sem gravar nada sem confirmação.
- **Cronograma (decisão sessão 075): NÃO persistir no `ipub.db`.** A planilha é o SSOT do cronograma e o usuário a edita manualmente — uma cópia local ficaria stale. `taxonomia_cronograma` segue alimentada apenas pelo pipeline de erros (`insert_questao.py`), sem relação de escrita com a planilha.
- 🔴 **Dois sinais, dois donos (`cronograma-contract.md` Cláusula 5b).** **Conclusão** ("esta tarefa saiu da fila?") vem da coluna **`Realizada?`** do **Dashboard EMED 2026** — Sheets **nativo**, lido em **texto puro** por `read_file_content`, executável **pelo agente** em runtime. **Ordem** (a sequência que o usuário reordenou) vive só no `Cronograma de Reta Final.xlsx` binário e é **ritual do usuário**: `python tools/cronograma.py --sync-drive <path-local>`, **sem MCP**. Regra dura: **se a leitura precisa de bytes, ela não é do agente** — nenhum passo pode exigir binário via MCP. Faltando qualquer um dos dois sinais, seguir com **caveat honesto**, nunca em silêncio e nunca bloqueando.

### Estrutura mapeada — Cronograma de Reta Final.xlsx

> Esta seção descreve o arquivo que o **usuário** processa localmente no ritual `--sync-drive`. O agente **não** baixa este xlsx: `read_file_content` embola a grade e o caminho binário via MCP não fecha (defeito D5). Aba única `Plan1`:

- **Linha 2** — 28 semanas, colunas 1–28: `"30/03 a 03/04/26"` … `"05/10 a 09/10/26"` (⚠️ typo na semana 11: `"08/06 a 12/06/25"`, ano errado).
- **Linha 3** — trilha da semana: `GO` ×2 → `U/E` ×6 → `CIRURGIA` ×7 → `OPCIONAL` ×7 → `CLÍNICA 2` ×6.
- **Linhas 4–16** — slots de tarefas da semana, formato `"Tema (Tipo)"` com quebras de linha internas (normalizar whitespace). Tipos: `Teoria [I-IV]`, `Revisão [I-II]`, `Revisão por Questões` (blocos multi-tema separados por `;`). Linhas 4–8 tendem a seguir trilhas fixas (Preventiva, Pediatria, Cirurgia, GIN, OBS); 9–16 são mistas/esparsas.

Para localizar a semana corrente: comparar a data de hoje com os ranges da linha 2. Os temas do cronograma casam com os `Assunto` das abas do Dashboard — a conciliação tarefa-a-tarefa entre as duas planilhas é possível por (tema, tipo).

**Marcador de conclusão (workflow do usuário):** o usuário **risca / muda a cor** do tema no cronograma ao concluí-lo (lê + faz exercícios, lança no dashboard). A formatação só é legível pelo **binário local**, no ritual do usuário — `cronograma.py --sync-drive` lê `cell.fill.fgColor.rgb` (cor de fundo) e `cell.font.strike` (tachado) via `openpyxl`; célula sem preenchimento/sem strike = pendente. **O agente não tem esse caminho**: o sinal de conclusão que ele lê é a coluna `Realizada?` do Dashboard EMED (texto puro). Ver `core/contracts/reconcile-contract.md §Absorção de dados de performance` e `cronograma-contract.md` Cláusula 5b.

---

## Fluxo

1. **Localizar a planilha.** Após autenticado, usar as tools do Google Drive MCP para encontrar e ler a planilha indicada pelo usuário (por nome ou link). Sheets pode ser exportado/lido como CSV/tabela.
2. **Mapear colunas.** A estrutura varia por planilha. Mapear para o shape canônico por linha:
   ```
   {sessao:int, area:str, feitas:int, acertos:int, data?:"YYYY-MM-DD", obs?:str}
   ```
   `sessao` é o número da sessão de estudo; se a planilha não tiver, combinar com o usuário (ex.: usar a sessão corrente ou uma sequência).
3. **Normalizar a área.** Converter o rótulo da planilha para um valor de `AREAS_VALIDAS` — **fonte única: `core/areas.json`, lida por `app/utils/areas.py`** (F89, s176; não é mais `registrar_sessao_bulk.py`). Ex.: "GO"→"Ginecologia"/"Obstetrícia", "Clínica/Cardio"→"Cardiologia". 🔴 Desde a s176 os 3 writers de taxonomia **recusam** área fora da lista (`AreaInvalida`, com o palpite mais próximo); rótulo que não casar é **reportado, nunca gravado errado** — e `GO`/`Clínica Médica` são ambíguos por natureza, então a decisão é sua, não do código.
4. **Gravar em lote.** Escrever as linhas mapeadas num JSON e chamar:
   ```bash
   python tools/importar_sessoes.py --rows-file <linhas.json>
   ```
   O importador valida cada linha (área válida, `acertos<=feitas`), pula duplicatas `(sessao, area)` por idempotência, e imprime resumo: **inseridas / puladas / inválidas**.
5. **Reportar.** Relayar o resumo ao usuário, listando explicitamente as linhas inválidas (área não reconhecida, números inconsistentes) para correção.
6. 🔴 **Gravar o snapshot — SEMPRE que ler a planilha, mesmo sem importar nada (B3/F35).** Este é o **único** momento em que os números da planilha existem; se eles não forem gravados agora, o reconcile W1 volta a depender de alguém lembrar de olhar — que é o achado. Passar as somas das **abas por disciplina** (autoritativas) e a data do **último lançamento dentro da planilha**:
   ```bash
   python tools/importar_sessoes.py --snapshot --por-area @abas.json --ultimo-lancamento 2026-07-20
   ```
   O boot passa a emitir uma linha por sessão (`Planilha x db (W1/F35)`) com o delta e a **idade da planilha**. Enquanto não houver snapshot, ele diz `NAO MEDIDO` — nunca assume delta zero.

---

## Contrato do CLI (`importar_sessoes.py`)

```bash
python tools/importar_sessoes.py --rows-file <path.json>
python tools/importar_sessoes.py --snapshot [--total N] [--por-area '{"Pediatria": 512}'|@abas.json] --ultimo-lancamento AAAA-MM-DD
python tools/importar_sessoes.py --show-snapshot
python tools/importar_sessoes.py --abandonada "<motivo>"
```

**Importação de volume:**
- `--rows-file`: JSON com lista de linhas no shape acima (UTF-8).
- Reusa `registrar()` — mesma idempotência e validação do registro manual.
- Não aborta o lote em linha inválida: reporta e segue.

**Snapshot da planilha (alimenta o reconcile W1; não importa volume):**
- `--snapshot`: grava `preparacao_estado.planilha_snapshot`. Exige `--ultimo-lancamento`.
- `--por-area`: somas das **abas por disciplina**, inline ou `@arquivo.json`. Quando presente, o `--total` é derivado da soma.
- `--total`: total declarado. Junto com `--por-area`, é **conferido** contra a soma — divergência é recusada com os dois números na mensagem (é o bug de fórmula do Quadro Geral, s075). Sozinho, grava sem detalhe por área e o boot declara que o mislabel de área **não foi verificado**.
- `--ultimo-lancamento AAAA-MM-DD`: data da última tarefa lançada **dentro** da planilha — é a *idade* dela, e responde "a planilha ainda é alimentada?". Data no futuro é recusada. Distinta de `lido_em` (idade da nossa cópia), gravada sozinha.
- `--show-snapshot`: imprime o snapshot gravado (JSON).
- `--abandonada "<motivo>"`: registra a resposta do operador a *"a planilha ainda é fonte?"*. O boot para de cobrar e passa a dizer **comparação suspensa**, preservando o último delta medido — muda o peso, não o mecanismo.
- Leitura do reconcile: `python tools/day_plan.py --planilha` (read-only, nunca bloqueia).

---

## Notas

- **Persistência canônica** continua em `sessoes_bulk` via `registrar()`. Este fluxo não cria caminho de dados paralelo.
- **Áreas válidas** são a fonte de verdade do vocabulário; normalizar sempre antes de gravar.
- Para registro pontual (uma sessão só, sem planilha), usar `tools/registrar_sessao_bulk.py` direto (ver `AGENTE.md` decisão "SSOT volumétrica").

---

## Assinatura canônica — `tools/registrar_sessao_bulk.py`

> **Portador canônico deste CLI** (`AGENTE.md §7.2`). É o **writer da SSOT volumétrica**
> (`sessoes_bulk`): ao ouvir *"fiz X questões, acertei Y"*, o agente chama isto **antes** de
> processar erros individuais. O `importar_sessoes.py` (lote a partir da planilha) é uma camada
> por cima deste writer, não um segundo caminho de escrita.

| Flag | Função |
|---|---|
| `--sessao N` | Número da sessão (ex.: 67). |
| `--area AREA` | Área clínica. Válidas: **`core/areas.json`** via `app/utils/areas.py` (F89) — writer **recusa** área fora da lista, com o palpite mais próximo. |
| `--feitas N` | Total de questões feitas. |
| `--acertos N` | Total de acertos. Validado: `acertos <= feitas`. |
| `--data YYYY-MM-DD` | Data da sessão (default: hoje). 🔴 Quando o estudo e o registro caem em dias diferentes, informar a data **do estudo**. |
| `--obs "..."` | Observação livre (ex.: *"Bloco ATLS"*). |
| `--acumular` | **F22:** soma este bloco a um registro existente da mesma `(sessao, area)` em vez de recusar — é o 2º bloco do mesmo dia, não uma duplicata. |
| `--semana N` | Atualiza no mesmo ato a **posição SSOT** (semana de conteúdo) — ver `preparacao.py` em `engenharia-cli.md`. |
- O read da planilha é responsabilidade do agente via MCP; o código nunca lê o Drive sozinho.
