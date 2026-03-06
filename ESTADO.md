# ESTADO — IPUB (Preparação para Residência Médica)
*Atualizado: 2026-03-06 (sessão 007) | Ferramenta: Antigravity*

---

## O que é este projeto

Ambiente de estudo para residência médica. Processa questões de prova, registra padrões de erro em `caderno_erros.md`, e mantém resumos clínicos organizados por área/tema em `Temas/`. Portável para qualquer LLM via workflows em `.agents/workflows/`.

---

## Estado atual

**Operação contínua** — cada sessão processa questões e/ou cria resumos.

- **45 entradas** no caderno de erros (5 áreas)
- **21 resumos** em `Temas/` — incluindo `Infectologia/TB.md` e `HIV.md` (consolidados)
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

- `caderno_erros.md` atualizado a CADA questão — nunca em batch
- `progresso.md` derivado do caderno — atualizar junto
- Protocolo de análise (`Tools/comando de analise de questao.md`) carregado ANTES de analisar qualquer questão
- Resumos seguem spec em `Tools/estilo-resumo.md` — bullets hierárquicos, ⭐/⚠️/🔴; **sem tabelas, sem fluxogramas ASCII**
- Sessions numeradas globalmente em `history/` — qualquer agente registra
- Fichas/ e Memorex/ contêm PDFs valiosos — não deletar
- `extract_pdfs.py` é CLI genérica — não criar scripts de extração ad hoc
- Pasta `Extracted/` não existe mais — extrações vão para `%TEMP%` e são deletadas ao final do workflow
- Ao finalizar resumo: executar `--delete-pdfs <pasta_do_tema>` e `--delete-temps <paths_tmp>`

---

## Para retomar: leia nesta ordem

1. **Este arquivo** (`ESTADO.md`) — estado atual
2. **Workflow relevante** em `.agents/workflows/` — o que fazer agora
3. `Tools/estilo-resumo.md` — se for criar/editar resumo
4. `Tools/comando de analise de questao.md` — se for analisar questões
5. Sessão mais recente: `history/session_007.md`

---

## Contexto do repositório

```
GitHub: github.com/daanmt/IPUB
Local:  C:\Users\daanm\IPUB
```

*Ao final de cada sessão: atualizar este arquivo e registrar em `history/`.*
