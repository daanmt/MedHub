---
description: "Ingere o volume de questões das planilhas do Google (via Google Drive MCP) para sessoes_bulk, substituindo a extração manual de xlsx. O agente lê e mapeia; tools/importar_sessoes.py persiste."
type: skill
layer: commands
status: canonical
---

# Skill: Importar Planilha

Ingere o volume de questões a partir de uma planilha do Google (Sheets/xlsx no Drive) para a tabela `sessoes_bulk` do `ipub.db`. Coerente com a tese agent-first: **o agente lê e interpreta a planilha via MCP; o código (`tools/importar_sessoes.py` → `registrar_sessao_bulk.registrar`) persiste**.

Use quando o usuário pedir: "importa minha planilha", "puxa as questões do Drive", "atualiza o volume a partir da planilha do EMED".

---

## Pré-requisito: autenticar o Google Drive MCP

O connector `claude.ai Google Drive` exige OAuth interativo. Se ainda não autenticado, instruir o usuário:

> Rode `/mcp` e selecione **"claude.ai Google Drive"** para autenticar.

Sem isso, as tools de leitura do Drive não ficam disponíveis. (O caminho de persistência local funciona independentemente.)

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
