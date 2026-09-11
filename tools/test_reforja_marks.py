"""B2 / F40+F41+G7 (s176): a fila de reforja como ESTADO, com fechamento VERIFICADO.

Spec: `.vibeflow/specs/fila-de-reforja-como-estado.md`.

As tres medicoes que motivaram a spec, e que estes testes travam:

1. **A cifra nunca foi a mesma duas vezes.** G7 registra 12 / 13 / 15 / 38 em sessoes diferentes.
   Quatro numeros para a mesma pergunta = contagem que sai de leitura humana.
2. **Marcar nao faz nada.** #792 foi marcado em TRES sessoes e esta em `card_version = 1`.
3. 🔴 **Reforjar nao prova que resolveu.** F82: #321 em v2 com o defeito intacto. E a s176 mediu
   o caso mais duro -- #1568 tem evento `reforja` de 2026-09-09 (v1 -> v2, campos
   `frente_pergunta` e `verso_*`) e CONTINUA disparando `checar_contrafactual_mal_formado`.
   Alguem reescreveu a pergunta e o defeito sobreviveu a reescrita.

Dai o invariante central: **nenhum sinal de "alguem editou" fecha uma marca.** Nem `card_version`,
nem o evento de reforja, nem a palavra de quem editou -- so a RE-VERIFICACAO do defeito.

Fixtures hermeticas: schema canonico via `init_db` em tmp_path; o texto do #1568 entra verbatim,
para o teste nao depender do `ipub.db` local.
"""
import contextlib
import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from app.utils import db  # noqa: E402
import init_db  # noqa: E402

# Verbatim do #1568 -- o card que foi reforjado em 09-09 e continua defeituoso.
CTX_1568 = ("Homem em uso de alopurinol ha algumas semanas, com rash maculopapular difuso, "
            "febre, adenomegalia e edema de face e maos.")
PERG_1568 = ("Qual achado cutaneo-mucoso, AUSENTE nesse quadro, afastaria DRESS e fecharia "
             "Stevens-Johnson?")
# Verbatim do #792 -- mesmo desenho, mas BEM-formado (traz o "se presente").
PERG_792 = "Qual achado, se presente durante o episodio, aponta para crise NAO epileptica?"


@pytest.fixture
def banco(tmp_path, monkeypatch):
    caminho = str(tmp_path / "ipub.db")
    monkeypatch.setattr(init_db, "DB_PATH", caminho)
    with contextlib.redirect_stdout(io.StringIO()):
        init_db.init_db()
    monkeypatch.setattr(db, "DB_PATH", caminho)
    conn = db.get_connection()
    conn.execute("INSERT INTO taxonomia_cronograma (id, area, tema) VALUES (1, 'Dermato', 'Farmacodermias')")
    # #1568 com o defeito INTACTO, ja em card_version=2 (foi reforjado e nao resolveu)
    conn.execute("INSERT INTO flashcards (id, tema_id, tipo, frente_contexto, frente_pergunta, "
                 "verso_resposta, card_version, quality_source) "
                 "VALUES (1568, 1, 'conteudo', ?, ?, 'Sinal de Nikolsky.', 2, 'qualitative')",
                 (CTX_1568, PERG_1568))
    # #792: mesmo eixo, pergunta bem-formada
    conn.execute("INSERT INTO flashcards (id, tema_id, tipo, frente_contexto, frente_pergunta, "
                 "verso_resposta, card_version, quality_source) "
                 "VALUES (792, 1, 'conteudo', 'Adolescente com movimentos generalizados.', ?, "
                 "'Olhos fechados resistindo a abertura.', 1, 'qualitative')", (PERG_792,))
    # #243: defeito 'pacote de fatos', que NENHUM predicado mede -- a fronteira declarada.
    conn.execute("INSERT INTO flashcards (id, tema_id, tipo, frente_contexto, frente_pergunta, "
                 "verso_resposta, card_version, quality_source) "
                 "VALUES (243, 1, 'conteudo', '', 'Quais os passos do damage control?', "
                 "'Tamponar, ressecar, peritoneostomia, reoperar em 48h.', 4, 'qualitative')")
    conn.commit()
    conn.close()
    return caminho


# ---------------------------------------------------------------------------
# 1. Append-only: marcar 3x sao 3 LINHAS, e o estado e derivado
# ---------------------------------------------------------------------------
def test_marcar_tres_vezes_produz_tres_linhas_e_a_fila_conta(banco):
    """🔴 O #792 deixa de ser anedota de HANDOFF e vira COUNT."""
    for _ in range(3):
        db.marcar_reforja(792, "contrafactual_mal_formado", origem="s176")
    fila = db.fila_reforja()
    assert len(fila) == 1, "3 marcacoes do MESMO par sao uma entrada de fila, nao tres"
    assert fila[0]["n_marcacoes"] == 3
    assert fila[0]["aberta"] is True


def test_nao_existe_coluna_booleana_de_status(banco):
    """A licao do F82 aplicada ao schema: nao pode haver campo que alguem 'vire'."""
    conn = db.get_connection()
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(reforja_marks)")}
    finally:
        conn.close()
    assert "evento" in cols
    for proibida in ("status", "resolvido", "fechado", "done", "ativo"):
        assert proibida not in cols, (
            f"coluna '{proibida}' reintroduz o estado mutavel que a spec proibe -- "
            "o estado e DERIVADO dos eventos")


def test_marca_sem_motivo_e_recusada(banco):
    with pytest.raises(ValueError):
        db.marcar_reforja(792, "   ")


# ---------------------------------------------------------------------------
# 2. 🔴 Fechamento VERIFICADO -- o coracao da spec
# ---------------------------------------------------------------------------
def test_fechar_e_recusado_enquanto_o_predicado_ainda_dispara(banco):
    """O caso #1568, verbatim: reforjado em 09-09 (v1->v2) e ainda defeituoso hoje.

    Este e o teste que impede a fila de virar teatro. Sem ele, 'fechei a marca' significa
    'alguem digitou alguma coisa' -- que e exatamente o que produziu #321 em v2 com o defeito
    intacto e #1568 em v2 disparando o predicado.
    """
    db.marcar_reforja(1568, "contrafactual_mal_formado", origem="s175")
    with pytest.raises(db.ReforjaAindaDefeituosa) as exc:
        db.fechar_reforja(1568, "contrafactual_mal_formado")
    assert "contrafactual_mal_formado" in str(exc.value)
    assert db.fila_reforja()[0]["aberta"] is True, "a marca tem de CONTINUAR aberta"


def test_card_version_2_nao_fecha_nada(banco):
    """Explicito porque foi a inferencia que o F82 derrubou: o #1568 do fixture ESTA em
    card_version=2 e mesmo assim o fechamento e recusado. Versao nao e evidencia."""
    conn = db.get_connection()
    try:
        v = conn.execute("SELECT card_version FROM flashcards WHERE id=1568").fetchone()[0]
    finally:
        conn.close()
    assert v == 2
    db.marcar_reforja(1568, "contrafactual_mal_formado")
    with pytest.raises(db.ReforjaAindaDefeituosa):
        db.fechar_reforja(1568, "contrafactual_mal_formado")


def test_fechar_passa_quando_o_defeito_saiu_de_verdade(banco):
    """Reescrever a pergunta com o condicional resolve -- e AI o fechamento passa,
    gravando QUAL evidencia o fechou."""
    db.marcar_reforja(1568, "contrafactual_mal_formado")
    db.update_flashcard_fields(1568, {"frente_pergunta":
                                      "Qual achado cutaneo-mucoso, se estivesse presente, "
                                      "fecharia Stevens-Johnson em vez de DRESS?"})
    db.fechar_reforja(1568, "contrafactual_mal_formado")
    fila = db.fila_reforja(incluir_fechadas=True)
    assert fila[0]["aberta"] is False
    conn = db.get_connection()
    try:
        ev = conn.execute("SELECT evidencia FROM reforja_marks WHERE evento='fechada'").fetchone()[0]
    finally:
        conn.close()
    assert "re-rodou limpo" in ev


def test_forcar_exige_justificativa_e_ela_fica_gravada(banco):
    db.marcar_reforja(1568, "contrafactual_mal_formado")
    with pytest.raises(ValueError):
        db.fechar_reforja(1568, "contrafactual_mal_formado", forcar=True, justificativa="  ")
    db.fechar_reforja(1568, "contrafactual_mal_formado", forcar=True,
                      justificativa="banca cobra assim; defeito aceito conscientemente")
    conn = db.get_connection()
    try:
        ev = conn.execute("SELECT evidencia FROM reforja_marks WHERE evento='fechada'").fetchone()[0]
    finally:
        conn.close()
    assert ev.startswith("forcado:") and "banca cobra assim" in ev


# ---------------------------------------------------------------------------
# 3. `descartada` e estado de primeira classe
# ---------------------------------------------------------------------------
def test_descartar_e_diferente_de_fechar(banco):
    """'Olhei e nao era defeito' nao pode contar como conserto -- senao a metrica de
    passivo mente para cima."""
    db.marcar_reforja(792, "contrafactual_mal_formado")
    db.descartar_reforja(792, "contrafactual_mal_formado",
                         "a pergunta traz 'se presente': e bem-formada")
    fila = db.fila_reforja(incluir_fechadas=True)
    assert fila[0]["aberta"] is False
    assert fila[0]["descartada"] == 1 and fila[0]["fechada"] == 0


def test_descartar_exige_justificativa(banco):
    db.marcar_reforja(792, "x")
    with pytest.raises(ValueError):
        db.descartar_reforja(792, "x", "")


# ---------------------------------------------------------------------------
# 4. Fronteira DECLARADA: motivo sem predicado fecha por palavra humana
# ---------------------------------------------------------------------------
def test_motivo_sem_predicado_fecha_como_humana_e_a_linha_diz_isso(banco):
    """Nem todo defeito tem predicado. 'pacote_de_fatos' nao tem -- e o fechamento
    grava `evidencia='humana'` em vez de fingir verificacao."""
    db.marcar_reforja(243, "pacote_de_fatos")
    db.fechar_reforja(243, "pacote_de_fatos")
    conn = db.get_connection()
    try:
        ev = conn.execute("SELECT evidencia FROM reforja_marks WHERE evento='fechada'").fetchone()[0]
    finally:
        conn.close()
    assert ev == "humana"


# ---------------------------------------------------------------------------
# 5. O backfill declara o COUNT antes de escrever, e nao inventa estado
# ---------------------------------------------------------------------------
def test_backfill_so_migra_marcas_com_proveniencia():
    """🔴 O 'passivo ~37' do HANDOFF NAO entra: existe o numero, nao existe a lista.

    Fabricar 37 linhas a partir de um numero sem nomes seria inventar estado -- a propria
    doenca que esta fila cura.
    """
    import reforja
    assert len(reforja.BACKFILL) == 9
    assert all(origem.strip() for _, _, origem in reforja.BACKFILL), \
        "toda linha do backfill carrega a proveniencia de onde a marca vivia"
    assert sum(1 for c, _, _ in reforja.BACKFILL if c == 792) == 3, \
        "#792 entra 3x -- e o dado que prova que marcar nao move o card"
