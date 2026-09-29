"""test_selo_rotacao.py -- a ROTACAO do ledger (spec ledger-rotacao-part-1, s204).

Decisao do operador em 28/09/2026: "o que resolvermos, sai da frente". O que esta
suite trava, em ordem de risco:

1. **Nenhum texto se perde.** O bloco do achado viaja inteiro: o sha256 de cada
   bloco e o mesmo antes e depois, e o que nao e bloco de achado fica onde estava.
2. **So o resolvido sai.** FEITO, SUPERADO e RETRATADO saem da frente; MITIGADO e
   PARCIAL ficam (tem residuo declarado), assim como GATE, DECLARADO e ABERTO.
3. **Dry-run e COUNT-ASSERT.** Sem `--apply` nada e escrito; `--apply` sem
   `--expect` igual ao N medido recusa e nao escreve.
4. **O selo mostra TUDO que esta aberto.** Ate a s204 a saida padrao nao imprimia
   GATE nem DECLARADO: 12 achados ficavam invisiveis.

Ledger sintetico em `tmp_path` -- o `AUDITORIA_MEDHUB.md` real nunca e tocado.

LIMITE DECLARADO: a suite prova o MOVER. Ela nao julga se o status escrito no
cabecalho e verdadeiro -- cabecalho que mente leva o bloco para o lugar errado, e
quem pega isso sao os checks de status (G14, G14b) do `consistencia_check`.
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import selo  # noqa: E402

FRENTE = """---
type: report
---

# Ledger de teste

Preambulo que fica na frente.

<!-- selo:indice:inicio -->
<!-- selo:indice:fim -->

### F9 -- item novo aguardando triagem -- **MEDIA** -- **DECLARADO (s204) -- remedio proposto, aguarda triagem do /ai-eng**

- corpo do F9

### F8 -- pergunta ao dono -- **MEDIA** -- **GATE (operador decide o rumo)**

- corpo do F8

### F7 -- mitigado com residuo -- **BAIXA** -- **MITIGADO (s186); a causa de fundo fica DECLARADA**

- corpo do F7

### F6 -- fechado com bloco de codigo -- **ALTA** -- **RESOLVIDO (s200)**

- corpo do F6

```
# isto NAO e cabecalho: esta dentro de cerca de codigo
### F99 -- nem isto
```

- fim do F6

### F5 -- parcial -- **MEDIA** -- **PARCIAL (mecanismo feito, conteudo aberto)**

- corpo do F5

### F4 -- o sujeito sumiu -- **BAIXA** -- **SUPERADO (s150)**

- corpo do F4

### F3 -- com continuacao -- **MEDIA** -- **RESOLVIDO (s165)**

- corpo do F3

### F3 -- atualizacao (s165)

- continuacao do F3, sem status proprio

### F2 -- aberto de verdade -- **MEDIA** -- **ABERTO**

- corpo do F2
"""

HISTORICO = """# Ledger -- resolvidos

### F1 -- o primeiro -- **MEDIA** -- **RESOLVIDO (s108)**

- corpo do F1
"""


def _sha(texto):
    return hashlib.sha256(texto.strip().encode("utf-8")).hexdigest()


def _blocos_f(texto):
    return {(b["id"], i): _sha(b["texto"])
            for i, b in enumerate(b for b in selo.blocos(texto) if b["tipo"] == "F")}


def _ids(texto):
    return [b["id"] for b in selo.blocos(texto) if b["tipo"] == "F"]


def test_blocos_conservam_o_texto_inteiro_e_ignoram_cerca_de_codigo():
    partes = selo.blocos(FRENTE)
    assert "".join(b["texto"] for b in partes) == FRENTE, "particionar nao pode perder 1 byte"
    assert "F99" not in _ids(FRENTE), "cabecalho dentro de cerca de codigo nao abre bloco"
    f6 = next(b for b in partes if b["id"] == "F6")
    assert "- fim do F6" in f6["texto"], "a cerca de codigo nao pode partir o bloco do F6"


def test_rotacao_move_so_os_resolvidos_e_conserva_cada_bloco():
    antes = sorted(list(_blocos_f(FRENTE).values()) + list(_blocos_f(HISTORICO).values()))
    frente, historico, movidos = selo.rotacionar(FRENTE, HISTORICO, hoje="2026-09-28")
    assert movidos == ["F6", "F4", "F3"], movidos
    assert _ids(frente) == ["F9", "F8", "F7", "F5", "F2"]
    assert _ids(historico) == ["F1", "F6", "F4", "F3", "F3"]
    depois = sorted(list(_blocos_f(frente).values()) + list(_blocos_f(historico).values()))
    assert depois == antes, "o sha256 de cada bloco tem de sobreviver a mudanca"
    assert "Preambulo que fica na frente." in frente
    assert "## Rotacionados em 2026-09-28" in historico


def test_continuacao_viaja_com_o_pai():
    _, historico, _ = selo.rotacionar(FRENTE, HISTORICO, hoje="2026-09-28")
    assert "- continuacao do F3, sem status proprio" in historico
    i_pai = historico.index("### F3 -- com continuacao")
    i_cont = historico.index("### F3 -- atualizacao (s165)")
    assert i_pai < i_cont, "a continuacao segue o pai, na mesma ordem"


def test_mitigado_e_parcial_ficam_na_frente():
    frente, historico, _ = selo.rotacionar(FRENTE, HISTORICO, hoje="2026-09-28")
    assert "### F7 --" in frente and "### F5 --" in frente
    assert "### F7 --" not in historico and "### F5 --" not in historico


def test_rotacao_e_idempotente():
    frente, historico, _ = selo.rotacionar(FRENTE, HISTORICO, hoje="2026-09-28")
    frente2, historico2, movidos2 = selo.rotacionar(frente, historico, hoje="2026-09-29")
    assert movidos2 == []
    assert frente2 == frente and historico2 == historico, "2a rodada nao muda 1 byte"


def test_indice_lista_os_abertos_com_severidade_status_e_quem_decide():
    frente, historico, _ = selo.rotacionar(FRENTE, HISTORICO, hoje="2026-09-28")
    ini = frente.index(selo.MARCA_INDICE_INI)
    fim = frente.index(selo.MARCA_INDICE_FIM)
    indice = frente[ini:fim]
    assert "**Em aberto: 5**" in indice and "Resolvidos: 4" in indice
    for fid in ("F9", "F8", "F7", "F5", "F2"):
        assert "| %s |" % fid in indice
    assert "| F8 | MEDIA | GATE | operador |" in indice
    assert "| F9 | MEDIA | DECLARADO | /ai-eng |" in indice
    assert "| F7 | BAIXA | MITIGADO |" in indice, "na lista de abertos vale o nome do cabecalho"
    assert "| F6 |" not in indice


def _arquivos(tmp_path):
    frente = tmp_path / "AUDITORIA_MEDHUB.md"
    historico = tmp_path / "history" / "auditoria" / "resolvidos.md"
    historico.parent.mkdir(parents=True)
    frente.write_text(FRENTE, encoding="utf-8")
    historico.write_text(HISTORICO, encoding="utf-8")
    return frente, historico


def test_dry_run_nao_escreve(tmp_path, capsys):
    frente, historico = _arquivos(tmp_path)
    code = selo.rotacionar_arquivos(frente, historico, apply=False, hoje="2026-09-28")
    assert code == 0
    assert frente.read_text(encoding="utf-8") == FRENTE
    assert historico.read_text(encoding="utf-8") == HISTORICO
    assert "3 achado(s)" in capsys.readouterr().out


def test_expect_errado_recusa_sem_escrever(tmp_path, capsys):
    frente, historico = _arquivos(tmp_path)
    assert selo.rotacionar_arquivos(frente, historico, apply=True, expect=None,
                                    hoje="2026-09-28") == 2, "--apply sem --expect recusa"
    assert selo.rotacionar_arquivos(frente, historico, apply=True, expect=2,
                                    hoje="2026-09-28") == 2, "--expect diferente do medido recusa"
    assert frente.read_text(encoding="utf-8") == FRENTE
    assert historico.read_text(encoding="utf-8") == HISTORICO


def test_apply_com_expect_certo_escreve_os_dois(tmp_path):
    frente, historico = _arquivos(tmp_path)
    assert selo.rotacionar_arquivos(frente, historico, apply=True, expect=3,
                                    hoje="2026-09-28") == 0
    assert _ids(frente.read_text(encoding="utf-8")) == ["F9", "F8", "F7", "F5", "F2"]
    assert "### F6 --" in historico.read_text(encoding="utf-8")


def test_selo_lista_todo_item_em_aberto():
    achados = selo.achados_de(FRENTE, "frente") + selo.achados_de(HISTORICO, "historico")
    linhas = "\n".join(selo.linhas_em_aberto(achados))
    for fid in ("F9", "F8", "F7", "F5", "F2"):
        assert fid in linhas, "%s esta aberto e tem de aparecer" % fid
    assert "GATE" in linhas and "DECLARADO" in linhas, (
        "GATE e DECLARADO ficavam fora da saida padrao ate a s204")
    assert "F6" not in linhas and "F1" not in linhas


def test_onde_mora_cada_achado():
    achados = selo.achados_de(FRENTE, "frente") + selo.achados_de(HISTORICO, "historico")
    onde = {a["id"]: a["onde"] for a in achados}
    assert onde["F1"] == "historico" and onde["F9"] == "frente"
    assert len(achados) == 9, "a continuacao do F3 nao conta como achado novo"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
