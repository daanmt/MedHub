## Audit Report: Alça fechada v0 -- responder e assinar dentro do hub

> Auditado em 2026-10-04 (s213), subagente auditor. Spec: `.vibeflow/specs/alca-fechada-v0.md`. Relato: `tmp/alca_s213/ENTREGA.md`.
> Diff auditado = árvore de trabalho NÃO commitada: `core/templates/hub.html` (+259), `tools/test_hub_pendencias.py` (novo),
> `.claude/commands/hub-backend.md` (+ espelho), `pytest.ini`, `AGENTE.md` (§7.4, +31 -> +32), `artifacts/aula-autopsia-uerj-2021.html`;
> fora do git: `tmp/uerj2021/build_autopsia.py`, `tmp/uerj2021/pendencias_seed/*.json`. Fotos lidas uma a uma em `tmp/alca_s213/shots/`.
> Medições em `tmp/alca_s213/audit/` (`pytest.txt`, `auto_check.txt`, `forms.txt`, `absorvida_sobrescrita.js`).

**Verdict: PARTIAL** -- DoD 6/7 (o 7 falha só na letra: faltam fotos no escuro de 2 cenários); Critical Gate com **1 falha
reproduzida**: o envio sobrescreve item `absorvida` quando o estado do banco não chegou à página. Correção de ~4 linhas,
**obrigatória antes de publicar**. Restante = achados baixos.

### DoD Checklist

- [x] **1. Mecanismo genérico no leitor.** `hub.html:515` `preparar` chama `pendLigar(doc, quadro)`; `pendLigar` (`hub.html:722-760`)
  liga todo `form.pend[data-pend]`, lê `analises/pendencias/itens` com `where("origem","==",o)` (`hub.html:751`). `pendEstado`:
  `aberta`/nada = Pendente, `respondida` = "Respondida em dd/mm" + texto, `absorvida` = `readOnly`, botão oculto, retorno abaixo
  (`pendPintar`). Fotos `a_claro` (Pendente), `b_enviar_claro`/`c_recarregar_claro` (Respondida em 04/10 com o texto),
  `e_absorvida_escuro` (campo travado, "Absorvida em 04/10", caixa "Retorno do agente"). Testes: `test_estados_aberta_respondida_absorvida`,
  `test_documento_com_form_pend_e_ligado_pelo_quadro`.
- [x] **2. Gravação com merge e contador.** `pendRegistro` grava exatamente `{origem, ref, tipo, pergunta, resposta, status, respondida_em}`;
  `pendGravar` (`hub.html:645-650`) = `get` -> `update` se existe, `set` se não. Foto `dump_fluxo`: seed (`titulo`, `obrigatoria`,
  `criada_em`) preservado + `resposta`/`respondida_em`. Contador: `a_claro` "0 de 22", `b_enviar_claro` "1 de 22". Reenvio = botão
  "Atualizar". Testes: `test_registro_e_assinatura_na_forma_do_banco`, `test_contador_conta_respondida_e_absorvida`,
  `test_gravacao_faz_merge_lendo_antes` (este só verifica strings). Ver **C1**: "reenvio até `absorvida`" só vale se o estado chegou.
- [x] **3. Nunca perder texto.** `pendRascunho` em try/catch, chave `medhub.pend.<id>`; gravado no `input` (`hub.html:738`) e antes do
  banco; apagado só no `.then` (`hub.html:707`). Mensagem literal confere. Fotos `d_falha_claro` (texto fica, mensagem, "Reenviar") e
  `d2_falha_recarregar_claro` (recarregado com banco fora: texto volta, "Pendente · rascunho guardado neste aparelho, não enviado").
  Teste: `test_rascunho_vai_ao_aparelho_antes_e_sai_so_depois_da_gravacao`.
- [x] **4. Assinatura de leitura.** Bloco único no template (`hub.html:304-309`), `assinaAbrir`/`assinaEnviar` gravam `doc_<slug>` com
  `{origem, tipo:"documento", status:"assinado", assinado_em, comentario}`. Fotos `f_assinar_escuro` e `f2_assinado_recarregar_claro`
  ("Assinado em 04/10" + comentário vindo do banco). Teste: `test_leitor_tem_a_assinatura_uma_vez`.
- [x] **5. Autópsia.** Artefato: 66 `form.pend` = 22 `pergunta` + 44 `comentario`; os 3 primeiros = `t1793_30/44/47` com
  "fecha um erro sem card" (3x); ids únicos e só `[A-Za-z0-9_-]`; todos `disabled` com "Abra pelo hub para responder" (foto
  `g_solto_fora_do_hub`); `form_pend` do gerador escapa rótulo/atributos (`build_autopsia.py:253-265`). Seeds: 22 arquivos, conjunto
  de ids **igual** aos 22 `data-pend` de pergunta; `obrigatoria: true` só em q30/q44/q47. Nenhum `<script>` novo no artefato (o único é
  o dos filtros, pré-existente). Teste: `test_autopsia_tem_as_22_perguntas_com_as_que_travam_erro_primeiro`.
- [x] **6. Rito do backend.** `hub-backend.md:21` passo 2c com `<!-- CHECK: test_template_grava_pendencias_na_colecao_do_dono -->`
  (o teste existe, `test_hub_pendencias.py:66`). `sync_skills.py --check` -> "Paridade ... OK", rc 0. Ver R4/R5 (executabilidade).
- [ ] **7. Navegador real nos 6 cenários, claro E escuro; suíte; auto_check.** Suíte: **1373 passed** (`pytest tools/ -q`).
  `auto_check --changed` -> rc 0, PASSED; WARN pré-existentes (`CLAUSULA_ORFA_SUBIU` 128 > 127: `clausulas_check --por-portador` não
  lista `hub-backend.md` nem `AGENTE.md`; o audit `painel-rota-s213` já media 128 antes desta entrega). **Falha na letra:** fotos no escuro
  só de absorvida, comentário, assinatura e solto; enviar/recarregar/falha só no claro. Impacto baixo (as cores vêm de variáveis do tema),
  mas o DoD pede os dois.

### Critical Gate

- **FAIL -- C1. Sobrescreve item `absorvida`.** A trava é só de cliente: `pendEnviar` sai se `f.estado.travado` (`hub.html:699`) e
  `assinaEnviar` idem (`hub.html:797`), mas `f.estado` só vira `absorvida` quando o `onSnapshot` entrega. `pendGravar` lê o documento e
  **não olha o `status`** (`hub.html:649`). Reproduzido em node com a função real (`tmp/alca_s213/audit/absorvida_sobrescrita.js`):
  item `{status:"absorvida", retorno_agente:"card 812"}` vira `{status:"respondida", resposta:"nova", retorno_agente:"card 812", ...}`.
  Quando acontece: página aberta com o banco fora e reenviada depois, ou leitura negada/indisponível -- e a leitura por `where` numa
  coleção de 3 segmentos **nunca rodou no banco real** (Risco da própria spec), com o erro silenciado (`hub.html:756`, `:777`). Efeito: o
  `/hub-backend` vê `respondida` de novo e reabsorve (card duplicado possível). O mesmo vale para `doc_<slug>` absorvido.
- PASS -- DOM: tudo que vem do banco ou do documento entra por `textContent`/`.value` (`pendPintar`, `assinaPintar`, `f.ret`, `f.st`);
  nenhum `innerHTML` no bloco novo. CSS injetado (`pendEstilo`) é constante.
- PASS (com ressalva C1) -- Merge: `update` preserva campos semeados (foto `dump_fluxo`). Ressalva menor: o `update` reescreve
  `pergunta`/`origem`/`ref`/`tipo` com o valor do DOM (hoje idêntico ao seed, gerados pelo mesmo build).
- PASS parcial -- Falha não derruba: `pendDb` em try/catch e `then(ok, ok(null))`; gravação rejeitada cai no `.catch` com mensagem;
  `col.doc` dentro de `.then`. Mas: (a) `pendLigar` roda sem try/catch dentro de `preparar` (`hub.html:515`), antes de `medir` -- uma
  exceção síncrona deixaria o quadro sem altura (R2); (b) leitura falha é **silenciosa** (`hub.html:756`, `:777`): todos os campos
  aparecem "Pendente" sem aviso (alimenta C1).
- PASS -- `localStorage`: só em `pendRascunho`, try/catch, chave por id, conteúdo = o próprio rascunho.
- PASS (risco baixo) -- Caminho: o id vai a `col.doc(id)` sobre a coleção fixa `analises/pendencias/itens`; não há concatenação para fora
  do prefixo, e tudo sob `analises` é admin/admin. Um `data-pend` com `/` produziria subcaminho (ainda sob `analises`); `doc_<slug>` vem de
  `[^/]+\.html$`, sem `/`. Sem validação de id (R3). Documentos do hub são autorais do agente.
- PASS -- Regressão: o diff só acrescenta 1 linha em `preparar` e 2+2 em `abrirAula`/`fecharAula`; quadro "feito", player
  (`sessoes/<lote>/notas`), Listas e Painel intocados; suíte inteira verde, incluindo `test_hub*`, `test_player_js`, `test_notas_player`.
- PASS -- Sem mudança em `capabilities` (só `claude.use("db")`, travado em `test_template_grava_pendencias_na_colecao_do_dono`); sem
  script externo; `sticky`/`nowrap` = 0 na página montada; botões 44 px (`test_hub_montado_leva_a_alca_sem_quebrar_o_celular`).

### Achados de revisor

**ALTA (bloqueia publicação)**
- **C1** acima. Correção: em `pendGravar`, recusar quando o documento lido já está absorvido e repintar com o dado do banco.

**MÉDIA**
- **R1. Leitura falha em silêncio** (`hub.html:756`, `:777`). Com o `where` sem prova no banco real, a 1a falha mostraria 22 "Pendente"
  vazios sem explicação. Correção: no callback de erro, pôr em cada `[data-pend-estado]` "Não consegui ler as respostas salvas." (e no
  `#hub-assina-st`).

**BAIXA**
- **R2.** `pendLigar(doc, quadro)` sem try/catch em `preparar` (`hub.html:515`). Embrulhar; `medir` precisa rodar sempre.
- **R3.** Sem validação de `data-pend`: aceitar só `/^[A-Za-z0-9_-]{1,120}$/` em `pendLigar` (pula o form). Fecha subcaminho e chave
  de `localStorage` ambígua (`data-pend=""` -> `medhub.pend.`).
- **R4. Rito usa `ArtifactData update`**, sem precedente nos comandos (todos usam `set`). Se a ferramenta só tiver `set`, a absorção
  apaga `resposta` e o seed. Cláusula deve dizer: "update (merge); sem update, `set` do documento lido + os 3 campos".
- **R5. Seeds sem caminho para o banco.** Nenhum rito/ferramenta sobe `tmp/uerj2021/pendencias_seed/` (a regra "aberta há mais de 7
  dias" e `obrigatoria` ficam inertes até alguém semear). O hub funciona sem seed (cai no `set`). Dizer no rito quem semeia e quando,
  junto da 1a `ArtifactData list` real (Risco da spec).
- **R6. Terminal fraco do 2c:** o CHECK aponta um teste do template (coleção), não a conduta do rito. Honesto seria
  `NAO-VERIFICAVEL` (com data) para "absorver e gravar retorno" ou um teste que leia o 2c.
- **R7. Rascunho perdido em edição durante "Salvando…"**: o textarea segue editável e o `.then` apaga a chave inteira
  (`hub.html:707`, `:803`). Apagar só se o valor salvo == valor atual.
- **R8. Peso visual:** os 44 comentários estão recolhidos dentro dos cards (foto `c2_comentario_escuro`, cards com "+") -- OK. Mas as 22
  perguntas abertas somam ~300 px cada (~6.600 px no celular, fotos `a`/`d`). Produto: considerar recolher as 19 não obrigatórias.
- **R9. Rodapé desalinhado:** `#hub-assina` vai de 16 a 374 px, a coluna do documento de 32 a 358 (`f_assinar_escuro`). Cosmético.
- **R10.** `PEND.pronto` memoriza `null` (`hub.html:635`): se o `db` não vier na 1a vez, "Reenviar" falha até recarregar a página.

Usabilidade 390 px (fotos): alvos 44 px, nada estoura, mensagem de erro quebra em 3 linhas sem empurrar o botão, estados legíveis no
escuro (verde/âmbar/vermelho sobre fundo escuro), absorvida claramente travada.

### Prompt-pack incremental (C1 + R1 + R2; ≤ 2 arquivos)

```
Arquivos: core/templates/hub.html, tools/test_hub_pendencias.py. Nada mais.
1. pendGravar(id, dados): no then do get, se s.exists e (s.data()||{}).status === "absorvida", rejeitar com
   um Error marcado (e.travado = true) e devolver o dado lido (e.item = s.data()). Não chamar update/set.
2. pendEnviar: no catch, se err.travado -> f.erro = false; f.ctx.itens[f.id] = err.item; pendRascunho(f.id, null);
   pendPintar(f, err.item); pendContar(f.ctx); return. Senão, o caminho atual. assinaEnviar: idem com ASSINA.item.
3. Callback de erro dos dois onSnapshot (pendLigar e assinaAbrir): escrever "Não consegui ler as respostas salvas."
   no [data-pend-estado] de cada form daquela origem que não esteja em erro, e no #hub-assina-st.
4. preparar: try{ pendLigar(doc, quadro); }catch(e){} (medir roda depois, sempre).
5. Teste novo (node, função REAL extraída, banco falso como em tmp/alca_s213/audit/absorvida_sobrescrita.js):
   test_gravar_nao_sobrescreve_absorvida -- doc absorvido segue absorvido e a promessa rejeita com travado.
DoD: (a) o teste novo passa e falha se o guard sair; (b) pytest tools/ verde; (c) auto_check --changed PASSED;
(d) foto escuro de falha e de enviar (fecha o DoD 7); (e) nenhuma outra linha do template muda.
```
