# Spec: Feedback por elo declarado -- part 1b: conferência do comentário do EMED pela API (BLOQUEADA)

> Escrita em 2026-10-02 (s211), desmembrada da part-1 no mesmo dia.
> **Status: BLOQUEADA -- espera o operador.** O classificador de permissões do harness negou, em 02/10/2026, a edição que acrescenta o flag em `tools/emed_api.py` (motivos declarados: `[PII Data Handling]` no bloco do `main()`; `[Instruction Poisoning]` na `description` do argparse). Regra da casa: negação = parar; quem destrava é o operador, configurando o classificador no settings de USUÁRIO com o contexto da decisão. Nenhum agente implementa esta spec por outro caminho, outro arquivo ou outra sessão enquanto isso.

## Objetivo

O agente principal consegue ler, sob demanda, o comentário do professor de UMA questão de uma lista do EMED, só em stdout, para conferir uma dúvida sobre as habilidades da cadeia -- sem gravar o comentário em lugar nenhum.

## Contexto

Decisão do operador em 02/10/2026: *"Em caso de dúvidas sobre as habilidades, você pode CONFERIR o comentário/resolução do EMED via api, bem como checar nas apostilas/resumos, e criar a nossa própria sequência - desta forma nos mantemos autorais."* Ela reverte em parte a de 26/09: o brief tem a REGRA DURA "sem ler o comentário do professor" e `tools/emed_api.py` garante por teste que o comentário "morre em memória -- nunca em disco, log, `tmp/`, stdout".

Enquanto esta spec não entra, vale o que já existia: a cadeia sai de resumos, apostilas e `/pesquisar-evidencia`; onde o raciocínio não chega ao gabarito, a solução marca `divergente` + `conferir`, e quem confere o professor é o operador, na plataforma.

**Fricção que esta spec remove:** o operador abrir a plataforma para conferir cada divergência -- viciosa.

## Definition of Done

1. `python -X utf8 tools/emed_api.py --lista tN --comentario NUM` imprime em stdout SÓ o texto do comentário do professor da questão NUM (`solution.sanitized_complete`, via `html_para_texto`); nada chega a disco. Teste: `test_comentario_sai_so_em_stdout_e_nada_em_disco`.
2. `--comentario` junto de `--apply` ou `--out`, ou com NUM < 1, é erro de uso (exit 1) antes de qualquer chamada de rede. Teste: `test_comentario_recusa_com_apply_ou_out`.
3. Campo ausente no item = `RECUSA:` que cita o NOME da chave e manda rodar `--esquema`, nunca um valor. Teste: `test_comentario_sem_o_campo_e_recusa_nomeada`.
4. `test_propriedade_nada_alem_da_whitelist_chega_a_disco_ou_saida` segue verde para todos os outros caminhos.
5. Rito de revogação (`AGENTE.md §10.10`) de "sem ler o comentário do professor" no mesmo commit: lápide no brief, em `.claude/commands/banco-emed.md` (§Solução MedHub e §`emed_api.py`) e na docstring do script; termo no registro do gate (`docs/MEMORIA-AUDITORIA.md` §12). O brief passa a dizer: o subagente de cunhagem NÃO chama a API, devolve "dúvidas de habilidade"; o PRINCIPAL confere uma a uma; o comentário nunca é copiado nem parafraseado para a cadeia.
6. `sync_skills --check` 0; gate D5 verde (flag na skill); suíte inteira verde; nenhum valor do comentário em recusa, log ou arquivo.

## Scope

**Arquivos (5):** `tools/emed_api.py` · `tools/test_emed_api.py` · `docs/SOLUCAO-MEDHUB-BRIEF.md` · `.claude/commands/banco-emed.md` (+ espelho) · `docs/MEMORIA-AUDITORIA.md` (1 linha).

O desenho das funções está no prompt pack do relatório `.vibeflow/audits/feedback-cadeia-declarada-part-1-audit.md`.

## Anti-scope

- Conferência em lote, cache do comentário, comentário em `tmp/`, no hub ou no git.
- Chamada da API por subagente.

## Technical Decisions

- **Stdout, uma questão por corrida:** o mínimo que permite conferir e mantém o resto da fronteira. Trade-off declarado: stdout entra no transcript local da sessão.

## Risks

- **O classificador pode manter a negação mesmo configurado:** aí a decisão volta ao operador (conferir na plataforma segue funcionando).
- **API interna sem contrato:** recusa nomeada + `--esquema`.

## Dependencies

- `.vibeflow/specs/feedback-cadeia-declarada-part-1.md`
- Configuração do classificador pelo operador.
