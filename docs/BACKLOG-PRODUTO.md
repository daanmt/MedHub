---
type: roadmap
layer: docs
status: canonical
relates_to: [HANDOFF, ROADMAP]
---

# Backlog de produto do MedHub

Uma linha por pedido ou feedback do operador, com origem e estado. Nada sai daqui sem estado final (`feito`, `descartado` com motivo) -- é o registro que impede uma ideia de se perder entre sessões. Decisão do operador em 05/10/2026 (s214): *"mantemos as ideias e feedbacks para sessão de engenharia, mas precisamos manter a rastreabilidade sobre todos eles, para não perdemos do roadmap. [...] precisamos fortalecer e muito a gestão de produto e para isso o ai-eng será fundamental."* Dono da gestão de produto: `/ai-eng` (handoff `~/ai-eng/HANDOFF-MEDHUB-produto-2026-10-05.md`). Estados: `aberto` · `em curso` · `feito vN` (validar com ele) · `pós-01/11` (ambiente próprio) · `descartado`.

## Hub e fluxo (pedidos dele)

| ID | Pedido | Origem | Estado | Próximo passo |
|---|---|---|---|---|
| P01 | Grifo (selecionar e destacar) também nas aulas | s214, 04/10 | feito v0 (Version 68) | validar seleção por TOQUE no celular |
| P02 | Editar texto/formatação das aulas "como no Notion" | s214 | pós-01/11 | ponte antes: "propor edição" pela alça fechada (ele reescreve, o agente aplica no `.md`) |
| P03 | Bloco **Teoria**: aulas + resumos dos temas; RD apontando para o resumo (links tipo Obsidian / grafo) | s214 | aberto | v0-2: Biblioteca + resumos da S4 (markdown + renderizador); link RD -> resumo explícito; memória `project_bloco_teoria` |
| P04 | Não perder o que foi revisado (aula/RD concluída some do hub) | s214 | aberto | parte do P03 (Biblioteca) |
| P05 | Assinar a leitura = concluir (sem clicar "feito" fora) | s214 | feito v0 (Version 67) | -- |
| P06 | Lista resolvida aparecer concluída sem esperar o backend | s214 | feito v0 (Version 67) | -- |
| P07 | Recolher semanas e blocos, deixando aberta só a que ele quiser | s214 | feito v0 (Version 68) | validar no celular |
| P08 | **Desconexão dashboard x banco x hub** ("desconfio que o dashboard não está syncado") | s214 | aberto, ENGENHARIA (/ai-eng) | causas medidas: Painel = foto do publish; backend manual; gesto duplicado (P05 resolveu). Falta: "Hoje ao vivo" (opção B aprovada em 28/09; **reafirmada por ele em 05/10, s216:** *"sem um backend dedicado, fazer com que o painel se atualizasse conforme questões/cards são feitos"*) e um desenho de sync sem tique manual. Viável sem backend: a página já grava `sessoes/<sessao>/notas`, `respostas/*` e `listas/*` no `db` do artifact e pode somá-los ao Painel ao abrir; o registro oficial (FSRS, plano) segue do tique |
| P09 | **Dia de estudo != dia do relógio**: lote começado num dia e terminado depois da meia-noite conta no dia em que começou | s214, 05/10 | aberto, ENGENHARIA (/ai-eng) | caso real: lote `2026-10-04a`, 70 de 150 notas depois de 00h; FSRS gravou o horário real; teto e Painel contam pelo relógio |
| P10 | Quadro de pendências (abertas -> respondidas -> absorvidas) no Painel; o ambiente como gestor tipo kanban/GPS | s213 | aberto | spec `alca-fechada-v0` §próximo; memória `feedback_alca_fechada_ambiente_gestor` |
| P11 | Produto próprio: backend, frontend, APIs, automações | s213-s214 | pós-01/11 | `docs/DISCOVERY-AMBIENTE-AGENTICO-2026-10-02.md` (fases 0-4); gargalos medidos na s214 viram requisitos |
| P12 | Gestão de produto forte, com o /ai-eng como dono do backlog | s214, 05/10 | aberto | este arquivo + handoff ao /ai-eng |
| P13 | **Reorganizar o hub em 3 blocos sem redundância:** *"painel = performance + cronograma + ritmo, bloco teoria = revisões + aulas do cronograma/tarefas pré-lista e bloco cards/questões de mão-na-massa"*; "Aulas" vira Teoria/Biblioteca e a gestão do cronograma passa ao Painel; motivo: *"evitar a redundância que ocorre hoje, de informação solta em tudo que é lugar"* | s215, 05/10 | PRD pronto (s216): `.vibeflow/prds/hub-integracao-cortar-passos.md`; 3 decisoes tomadas (4 abas na ordem Painel/Teoria/Listas/Cards; Documentacao so no Painel; Biblioteca daqui em diante) | medido: `docs/MEDICAO-HUB-3-BLOCOS-2026-10-05.md` (v0 = 4 fatias, ~145 linhas, ~25 testes, 1 sessão; sem dado novo); 3 decisões dele pendentes (4 x 3 abas; Documentação; Biblioteca retroativa); absorve P04 e o v0-2 do P03, toca P08 |
| P14 | **Assinar/marcar fecha a página e volta à anterior** (documento assinado, lista marcada como resolvida, feedback enviado): *"automaticamente aquela página fosse fechada e voltássemos para a página anterior"* | s216, 05/10 | aberto | hoje: assinar só pinta o botão (`hub.html` ~902) e concluir lista só troca o status (~1921); o leitor volta sempre para Aulas (medição P13 §2). v0 = após gravar com sucesso, `fecharAula()`/`qz-voltar` para a aba de ORIGEM (hash), com o status visível no item recém-concluído; ~30 linhas + ~4 testes; cabe na sessão do P13 (fatia F5) |
| P15 | **Princípio de produto (dele, 05/10):** *"os ganhos agora são de integração, remoção de redundâncias, cortar passos desnecessários, e priorizar 95% do tempo do usuário estudando, e não tendo dificuldades com a UI e uma UX ruim"* | s216, 05/10 | critério | régua de priorização do backlog até 01/11: cada item passa a declarar "passos que corta" ou "redundância que remove"; o que não corta passo nem remove redundância espera |

## Dívida de engenharia que apareceu (s214)

| ID | Item | Estado |
|---|---|---|
| E01 | Publish exige ler inteiro todo arquivo novo: `index.html` ~90 mil tokens por publish que muda lote/quadro (gargalo real do protótipo) | aberto (argumento para P11) |
| E02 | `test_cli_importavel` falha por corrida quando outro agente grava no `ipub.db` (barrou commit) | aberto |
| E03 | `emed_api.py` recusa lista com questão só em imagem ou certo/errado (t833 t376 t110 t805 t826) | aberto (ele faz no EMED por ora) |
| E04 | Solução MedHub v3 ausente nas 25 listas novas | aberto |
| E05 | `banco-emed.md` e memória dizem teto de 5.000 docs; a ferramenta informa 25.000 | aberto |
| E06 | `cobertura_conhecimento.py` chama de "semana corrente" a S17 da grade antiga | aberto |
| E07 | Grifo das questões e das aulas são dois mecanismos: unificar quando o ambiente próprio existir | pós-01/11 |
