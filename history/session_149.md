# Session 149 -- 3 Aulas-Base S15 (Artifact) + Contrato de Design de Artifact
**Data:** 2026-08-19
**Ferramenta:** Claude Code (Sonnet 5)
**Continuidade:** Sessão 148

---

## O que foi feito

- **Aula-base de Aleitamento Materno (Pediatria, D8)** entregue no chat, ancorada no PDF-fonte do EMED (o resumo existente, `Aleitamento Materno e Mastite Lactacional.md`, era `status: stub` cobrindo só ~15% do escopo real -- mastite/ingurgitamento). Escada de degraus completa: conceitos/duração/vantagens, fisiologia (lactogênese 3 fases), técnica, manutenção/armazenamento, problemas (mastite x ingurgitamento como discriminador comparativo), restrições/contraindicações (farmacocinética + lista absoluta/temporária/não-contraindica), leite materno x outros leites, banco de leite/IHAC/desmame.
- **Aulas-base de Parasitoses+IRAS (Infectologia) e do cluster Apendicite/Colecistite e Colangite/Diverticulite (Cirurgia)** geradas via 2 forks paralelos (leitura de PDF completa + checagem de resumo existente + calibração de degrau via `day_plan.py --difficulty`), consolidadas com a aula de Aleitamento num único Artifact Markdown ("Aulas-Base S15").
- **Usuário pediu override de dificuldade + reestruturação em árvore:** Parasitoses e Colangite subiram de D5 para D10 por nota soberana ("temas absolutamente prevalentes"), igualando os demais subtemas dos 2 blocos (todos D10). Bundles que compartilham mecanismo devem virar árvore -- tronco comum destrinchado primeiro, depois branches específicas sem re-derivar o tronco. 2 novos forks reescreveram as seções:
  - **Parasitoses D10:** tronco 1 (síndrome de Loeffler/NASA), tronco 2 (lógica de sufixo -ENDAZOL/-NIDAZOL), branches por parasita, tronco 3 pequeno para os protozoários (Giardíase/Amebíase). O fork corrigiu um erro real do rascunho D5 anterior: **Enterobius vermicularis e Trichuris trichiura NÃO fazem síndrome de Loeffler** (ciclo direto por ingestão de ovo, sem passagem pulmonar) -- diferente dos 4 nematódeos do mnemônico NASA. Virou um branch de contraste dedicado.
  - **Abdome Agudo D10 uniforme:** tronco principal (obstrução de lúmen/ducto -> estase -> inflamação -> +/- infecção -> +/- perfuração, com o ritual do discriminador que EXCLUI) + sub-tronco biliar (Diretrizes de Tokyo/TG18, diagnóstico definitivo sempre exige imagem) antes de bifurcar Colecistite x Colangite. Conteúdo D10 novo: síndrome de Mirizzi, íleo biliar (tríade de Rigler, síndrome de Bouveret), classificação de Strasberg da lesão iatrogênica de via biliar, grade completa Tokyo x ASA, Visão Crítica de Segurança (Critical View of Safety), colecistectomia subtotal (Torek).
- Guidance da árvore (tronco -> branches para bundles que compartilham mecanismo) registrada como padrão permanente em `feedback_bundled_cronograma_task_content` (memória), generalizando o que antes só cobria "não deixar subtema de fora".
- `/revisar` aberto: fila de 118 cards em 60 clusters. Priorizados fora da ordem padrão (atrasados->hoje->novos) os clusters **SUS** (Preventiva, 16 cards) e **Asma** (Pediatria/Pneumo, confirmada fragmentação em 4 variantes de tema: Asma, Asma na Infância, Asma - Exacerbacao, e a própria área Pneumo/Asma) -- ambos flagados na s148 por terem cards-remédio (`erros_frescos`) nunca mostrados que já causaram reincidência confirmada. Bloco 1 de 6 cards apresentado (3 SUS + 3 Asma); nenhum rating foi respondido/gravado nesta sessão.
- **Usuário validou a qualidade da aula de Aleitamento Materno** ("ficou absurda de boa") e abriu um novo contrato de sessão: aula-base passa a renderizar como **Artifact HTML com design real** (tabelas, listas, fluxogramas -- skill `frontend-design`), não Markdown liso. Motivo: o usuário apaga os artifacts da conta do time de conteúdo médico depois de usá-los (efêmeros por desenho), então o artifact pode receber tratamento de design "gasto" à vontade. Modelo nomeado explicitamente: o motor reusável já existente para a Autópsia dos Simulados (`tools/autopsia_template.py` -- 651 linhas, tokens de cor com dark-mode completo, tipografia responsiva -- + `tools/autopsia_simulados.py`, o gerador que lê o banco e preenche o template). Registrado em `feedback_aula_base_artifact_design_contract` (memória) + `HANDOFF.md` + `ESTADO.md` como frente de engenharia aberta (construir `tools/aula_template.py` equivalente), não bloqueante para a próxima aula-base.

## Padrões de erro identificados (se sessão de questões)
- N/A -- sessão sem volume de questões (usuário executa os 3 blocos de S15 real fora da sessão; resultado + análise de erros vêm na s150).

## Artefatos criados/modificados
- Artifact publicado (fora do repo, efêmero por desenho do usuário): "Aulas-Base S15" (Aleitamento Materno D8; Parasitoses D10 + IRAS D10; Apendicite D10 + Colecistite e Colangite D10 + Diverticulite D10, os 3 últimos em árvore).
- `HANDOFF.md` -- rotacionado (s149).
- `ESTADO.md` -- header + item 3 de "Próximos passos" atualizados (nova frente).
- Memória (fora do repo git, `~/.claude/projects/.../memory/`): `feedback_aula_base_artifact_design_contract.md` (novo), `feedback_bundled_cronograma_task_content.md` (estendido com a guidance de árvore), `MEMORY.md` (2 linhas de índice atualizadas).
- Nenhum arquivo em `resumos/` foi alterado nesta sessão -- os gaps identificados (Diverticulite Aguda incompleta; Parasitoses/IRAS/Apendicite Aguda/Colecistite e Colangite sem `.md`) ficam pendentes de reforja, listados em `HANDOFF.md`.

## Decisões tomadas
- Nota de dificuldade é soberana do usuário mesmo sem persistir em `taxonomia_cronograma` (tema-zero, linha ainda não existe -- `set_dificuldade` retorna `False` sem erro, por design; a nota governa a profundidade da aula agora e será persistida quando a linha nascer via `insert_questao`/`insert_card_base`).
- Bundles que compartilham mecanismo real (ex.: os 4 diagnósticos de abdome agudo) viram árvore; bundles que só coincidem no mesmo dia do cronograma sem mecanismo comum (ex.: Parasitoses + IRAS) mantêm capítulos independentes -- a árvore não é forçada onde não há tronco genuíno.
- Artifact de aula-base é HTML com design completo daqui pra frente, mas o SSOT de conteúdo permanece `resumos/` -- o artifact é camada de apresentação efêmera, nunca a fonte de verdade.

## Próximos passos (se houver)
- Ver `HANDOFF.md` -> Próximo passo imediato (registrar volume + analisar erros dos 3 blocos ao retornar; continuar `/revisar` da fila intocada; considerar construir `tools/aula_template.py`; reforjar resumos com o conteúdo D10 novo).
