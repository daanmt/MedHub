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
- **Cronograma:** ainda não há CLI de persistência para o cronograma. Na primeira importação real, mapear a estrutura da planilha e definir o caminho de escrita (novo CLI em `tools/`, nunca SQL direto pelo agente).

---

## Fluxo

1. **Localizar a planilha.** Após autenticado, usar as tools do Google Drive MCP para encontrar e ler a planilha indicada pelo usuário (por nome ou link). Sheets pode ser exportado/lido como CSV/tabela.
2. **Mapear colunas.** A estrutura varia por planilha. Mapear para o shape canônico por linha:
   ```
   {sessao:int, area:str, feitas:int, acertos:int, data?:"YYYY-MM-DD", obs?:str}
   ```
   `sessao` é o número da sessão de estudo; se a planilha não tiver, combinar com o usuário (ex.: usar a sessão corrente ou uma sequência).
3. **Normalizar a área.** Converter o rótulo da planilha para um valor de `AREAS_VALIDAS` (em `registrar_sessao_bulk.py`): ex. "GO"→"Ginecologia"/"Obstetrícia", "Clínica/Cardio"→"Cardiologia". Linhas que não casarem serão reportadas (não gravadas erradas).
4. **Gravar em lote.** Escrever as linhas mapeadas num JSON e chamar:
   ```bash
   python tools/importar_sessoes.py --rows-file <linhas.json>
   ```
   O importador valida cada linha (área válida, `acertos<=feitas`), pula duplicatas `(sessao, area)` por idempotência, e imprime resumo: **inseridas / puladas / inválidas**.
5. **Reportar.** Relayar o resumo ao usuário, listando explicitamente as linhas inválidas (área não reconhecida, números inconsistentes) para correção.

---

## Contrato do CLI (`importar_sessoes.py`)

```bash
python tools/importar_sessoes.py --rows-file <path.json>
```

- `--rows-file` (obrigatório): JSON com lista de linhas no shape acima (UTF-8).
- Reusa `registrar()` — mesma idempotência e validação do registro manual.
- Não aborta o lote em linha inválida: reporta e segue.

---

## Notas

- **Persistência canônica** continua em `sessoes_bulk` via `registrar()`. Este fluxo não cria caminho de dados paralelo.
- **Áreas válidas** são a fonte de verdade do vocabulário; normalizar sempre antes de gravar.
- Para registro pontual (uma sessão só, sem planilha), usar `tools/registrar_sessao_bulk.py` direto (ver `AGENTE.md` decisão "SSOT volumétrica").
- O read da planilha é responsabilidade do agente via MCP; o código nunca lê o Drive sozinho.
