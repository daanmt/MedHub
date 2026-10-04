# Spec: Alça fechada v0 -- responder e assinar dentro do hub

> Escrita em 2026-10-04 (s213). Pedido do operador no mesmo dia; sem PRD (mudança pequena, escopo fechado pelo agente principal).

## Objetivo

Toda pergunta que o agente faz num documento do hub ganha um campo de resposta com estado (Pendente, Respondida, Absorvida), e todo documento aberto no leitor pode ser assinado: a pendência passa a morar no banco do artifact, não no chat.

## Contexto

Citação do operador (04/10/2026): *"No 'Perguntas para você', seria interessante ter um local para inserir a resposta - e, com isso, toda pendência é resolvida, tal como num kanban; como você pode perceber, facilmente as tarefas se perdem [...] Sempre que o agente entregar uma demanda, documento/relatório/insight, ou mesmo lista, card, etc; tudo que é visto precisa ser 'assinado', como uma comunicação em alça fechada."*

A Autópsia UERJ 2021 tem 22 perguntas de uma linha (Q30, Q44 e Q47 travam o registro de um erro). Ele lê no celular e responderia no chat; a pendência se perde. Em 24/09 ele perdeu 64 de 90 notas de cards com o banco fora no celular: o texto digitado não pode depender da gravação dar certo.

**Fricção que esta spec remove:** pergunta do agente sem lugar de resposta, e documento entregue sem confirmação de leitura.

## Definition of Done

1. **Mecanismo genérico no leitor.** Documento aberto no hub com `form.pend[data-pend][data-origem][data-ref][data-tipo]` tem os campos ligados: o estado vem do banco (`analises/pendencias/itens`, filtrado por `origem`), `aberta` = Pendente, `respondida` = "Respondida em dd/mm" com o texto de volta, `absorvida` = campo travado com o `retorno_agente` abaixo. Teste: `tools/test_hub_pendencias.py`.
2. **Gravação com merge e contador.** Enviar grava `{origem, ref, tipo, pergunta, resposta, status: "respondida", respondida_em}` (update se o documento existe, set se não) e atualiza `[data-pend-contador]` ("N de M respondidas"). Reenvio permitido até `absorvida`.
3. **Nunca perder texto.** Rascunho espelhado em `localStorage` (`medhub.pend.<id>`, try/catch), restaurado ao abrir, apagado só depois da gravação confirmada; falha = texto fica + "Não salvou. O rascunho ficou guardado neste aparelho. Toque para reenviar."
4. **Assinatura de leitura** no rodapé do leitor do hub (uma vez, no template): grava `analises/pendencias/itens/doc_<slug>` = `{origem, tipo: "documento", status: "assinado", assinado_em, comentario}`; ao reabrir mostra "Assinado em dd/mm".
5. **Autópsia** (`tmp/uerj2021/build_autopsia.py`): 22 `form.pend` de pergunta (as 3 que travam erro primeiro, marcadas), um `form.pend` de comentário por questão, campos desabilitados fora do hub, seeds em `tmp/uerj2021/pendencias_seed/`.
6. **Rito do backend** (`/hub-backend`): passo "Pendências (alça fechada)" com terminal de cláusula; `sync_skills --check` 0.
7. **Conferido em navegador real** (Edge headless, 390 px, claro e escuro) nos 6 cenários; suíte inteira verde; `auto_check --changed` PASSED.

## Scope

`core/templates/hub.html` · `tools/test_hub_pendencias.py` · `tmp/uerj2021/build_autopsia.py` (fora do git) · `artifacts/aula-autopsia-uerj-2021.html` · `.claude/commands/hub-backend.md` (+ espelho).

## Anti-scope

- Quadro kanban no Painel, o gerador do Painel, CLI novo.
- Mudar a declaração de `capabilities` (a regra `analises` já fecha leitura e escrita ao dono e vale por prefixo).
- Tocar nos arquivos das aulas para a assinatura (ela mora no hub).

## Technical Decisions

- **Coleção `analises/pendencias/itens`:** caminho de 3 segmentos (coleção válida na gramática do banco, como `sessoes/<lote>/notas` do player); herda `read admin, write admin` da regra `analises`. As análises de lista (`analises/<lista>_<num>`) seguem como documentos diretos e não se misturam.
- **Merge = get + update/set:** o `set` do banco substitui o documento inteiro e o `update` exige que ele exista; ler antes preserva os campos semeados (`titulo`, `obrigatoria`, `criada_em`).
- **Estado padrão desabilitado no documento:** o arquivo solto não tem banco; o hub habilita ao ligar. Sem script no documento.
- **Funções puras (`pendEstado`, `pendDataCurta`, `pendContagem`)** testadas em node, como o `test_hub_render`.

## Applicable Patterns

- `tools/test_hub_render.py` (funções reais extraídas do template, rodadas em node).
- Espelho local do `qzGravar` (aba Listas): grava local primeiro, banco depois.

## Risks

- **Banco falso não é o banco real:** a gramática de caminho e a regra por prefixo vêm do contrato de tipos (0.2.54); a 1a gravação real precisa de uma leitura `ArtifactData list` de `analises/pendencias/itens` pelo agente principal.
- **Rascunho é por aparelho:** resposta digitada no celular e não enviada não aparece no PC.
