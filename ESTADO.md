# ESTADO — IPUB (Preparação para Residência Médica)
*Atualizado: 2026-03-11 (sessão 013) | Ferramenta: Antigravity*

---

Ambiente de estudo para residência médica. Processa questões de prova, registra padrões de erro em `caderno_erros.md`, e mantém resumos clínicos organizados por área/tema em `Temas/`. Portável para qualquer LLM via workflows em `.agents/workflows/`.

---

## INICIO OBRIGATÓRIO DE SESSÃO

**Leia `AGENTE.md` antes de qualquer ação.** Este arquivo contém o protocolo de boot e a ordem de leitura para garantir a continuidade do projeto.

- **63 entradas** no caderno de erros (5 áreas)
- **23 resumos** em `Temas/` — incluindo `Infectologia/TB.md`, `Pediatria/Emergências Pediátricas.md` e `Preventiva/Medidas de Saúde Coletiva.md`
- **3 workflows** operacionais em `.agents/workflows/`

---

## Mapa de artefatos

### Infraestrutura
| Artefato | Arquivo |
|---|---|
| Estado do projeto | `ESTADO.md` (este arquivo) |
| Workflows (3) | `.agents/workflows/*.md` |
| Especificação de formatação | `Tools/estilo-resumo.md` |
| Protocolo de análise | `Tools/comando de analise de questao.md` |
| Script extração PDF | `Tools/extract_pdfs.py` |
| Session logs | `history/session_NNN.md` |

### Conteúdo
| Artefato | Arquivo |
|---|---|
| Resumos clínicos | `Temas/{Área}/{Subespecialidade}/{Tema}.md` |
| Caderno de erros | `caderno_erros.md` (único, 36+ entradas) |
| Progresso | `progresso.md` |

### Material de referência (PDFs — não editáveis)
| Artefato | Pasta |
|---|---|
| Fichas de prova | `Fichas/` (5 PDFs por área) |
| Memorex por área | `Memorex/` (6 subpastas) |
| Textos extraídos | pasta temp do sistema (`%TEMP%`) — deletados ao final de cada sessão |

---

## Áreas com mais entradas no caderno

| Área | Entradas |
|---|---|
| Ginecologia e Obstetrícia | 13 |
| Pediatria | 11 |
| Medicina Preventiva | 7 |
| Cirurgia | 4 |
| Clínica Médica | 10 |

---

## Últimas sessões

**2026-03-11 | Antigravity (sessão 013):** Criação da seção de Trauma Abdominal em `Cirurgia/Trauma.md`. Inclusão de condutas para trauma contuso/penetrante, damage control, órgãos maciços/ocos, e armadilhas de prova.

**2026-03-10 | Antigravity (sessão 012):** Criação do resumo de `Pediatria/Emergências Pediátricas.md` (Arrritmias, PCR, TCE, Corpo Estranho e Afogamento). Foco em critérios PECARN e algoritmos PALS/Szpilman.

**2026-03-09 | Antigravity (sessão 011):** Criação do resumo de `[GIN] Rastreamento Colo.md` integrando diretrizes 2016 (Pap) e 2025 (DNA-HPV). Mapeamento de 34 "armadilhas de prova" baseadas em questões de residência.

**2026-03-09 | Antigravity (sessão 010):** Análise de 9 questões de Saúde Coletiva (indicadores de mortalidade). Atualização massiva do resumo de Preventiva e do caderno de erros (Total 59).

**2026-03-08 | Antigravity (sessão 009):** Análise de PTI (limiares e gravidade) e implementação da nova governança do projeto (`AGENTE.md`, `HANDOFF.md`, workflows refatorados).

**2026-03-06 | Antigravity (sessão 008):** Criação do resumo de `Hemostasia.md` a partir das apostilas `Hemost.pdf` e `Hemostasia_I__Co.pdf`. Consolidação de hemostasia normal, plaquetopatias, hemofilias, vW e trombofilias (SAF e hereditárias). Limpeza de arquivos temporários e PDFs da pasta do tema realizada.

**2026-03-06 | Antigravity (sessão 007):** Expansão massiva de Infectologia (`Tuberculose.md` e `HIV.md`) a partir de 6 apostilas/flashcards. Refinamentos baseados em erros de prova (transmissão vertical, neuro-semiologia, rastreio de TB). Deletados PDFs de infectologia após consolidação.

**2026-03-05 | Antigravity (sessão 006):** Eliminação da pasta `Extracted/`; `extract_pdfs.py` agora extrai para `%TEMP%` e possui `--delete-pdfs`/`--delete-temps` para limpeza automática pós-resumo. Workflow e `.gitignore` atualizados.

**2026-03-05 | Antigravity (sessão 005):** Consolidação de ferramentas — `estilo-resumo.md` movido para `Tools/`; `referencia/` removida; `extract_asma.py` deletado; `CLAUDE.md` e workflows atualizados. Proibição de tabelas e fluxogramas ASCII adicionada ao `Tools/estilo-resumo.md`.

**2026-03-05 | Antigravity (sessão 004):** Criação e refatoração de `Temas/Clínica Médica/Pneumologia/Asma.md` com GINA 2025 integrado. Reescrita do `Tools/extract_pdfs.py` com CLI genérica.

**2026-03-04 | Antigravity Opus (sessão 002):** Reestruturação lean — criou `history/`, `.agents/workflows/` (3 workflows), `referencia/estilo-resumo.md`, reformatou ESTADO.md como fonte de verdade, absorveu INSTRUCOES_AGENTE.md nos workflows. Criou resumo DM2 e reformatou para padrão IPUB. Deletou Cronograma/.

**Pré-002 | Diversas ferramentas (sessão 001):** Histórico retroativo — 21 resumos, 36 entradas no caderno, infraestrutura inicial. Ver `history/session_001.md`.

---

## Próximos passos

1. Continuar análise de questões por área (Asma é o tema atual)
2. Criar resumos para as áreas com menos cobertura em `Temas/`
3. Revisar padrões de erro periodicamente para reforço ativo

---

## Decisões críticas (não reverter)

- **Governança via AGENTE.md**: O boot e o fechamento seguem estritamente o `AGENTE.md`.
- `caderno_erros.md` atualizado a CADA questão — nunca em batch.
- `progresso.md` derivado do caderno — atualizar junto.
- Protocolo de análise (`Tools/comando de analise de questao.md`) carregado ANTES de analisar qualquer questão.
- Resumos seguem spec em `Tools/estilo-resumo.md` — bullets hierárquicos, ⭐/⚠️/🔴; **sem tabelas, sem fluxogramas ASCII**.
- Sessions numeradas globalmente em `history/` — qualquer agente registra.
- `extract_pdfs.py` é CLI genérica para extração para `%TEMP%`.

---

## Para retomar: leia nesta ordem

1. **`AGENTE.md`** —— Protocolo de boot.
2. **`HANDOFF.md`** —— Onde o último agente parou.
3. **`ESTADO.md`** —— Este arquivo (visão geral).

---

## Contexto do repositório

```
GitHub: github.com/daanmt/IPUB
Local:  C:\Users\daanm\IPUB
```

*Ao final de cada sessão: atualizar este arquivo e registrar em `history/`.*
