"""test_orquestrador.py -- testes da part-2 (recomendador do dia, PRD orquestracao).

Fixtures DETERMINISTICAS sobre a funcao pura recomendar_dia() + queries novas de
db (db temp) + paridade contrato<->CLI. Pytest-nativo (coleta direta); standalone:
python tools/test_orquestrador.py. Nada aqui toca o ipub.db real.
"""
import os
import re
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import app.utils.db as db  # noqa: E402
import day_plan as dp      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SINAIS_BASE = {
    "dias_enamed": 70, "restante_grade_q": 4000, "ritmo_real": 50.0,
    "vencidos": 3, "teto_efetivo": 30, "backlog_novos": 361,
    "semana_conteudo": 13, "lag": 3, "tema_alvo": "Apendicite Aguda",
    "frescos_tema_alvo": [],
}


def _tipos(reco):
    return [b["tipo"] for b in reco["blocos"]]


def test_mix_normal():
    r = dp.recomendar_dia(dict(SINAIS_BASE))
    tipos = _tipos(r)
    assert "questoes" in tipos and "fsrs" in tipos, f"mix basico (got {tipos})"
    assert "descanso" not in tipos and "simulado" not in tipos, \
        f"semana 13 nao-multipla e energia default: sem slots especiais (got {tipos})"
    assert len(r["justificativa"]) >= 3, "justificativa cita >=3 sinais"
    assert r["defaults_assumidos"] is True, "sem tempo/energia -> defaults declarados"
    pj = r["projecao"]
    # ritmo 50 q/dia, 4000 restantes -> 80d para fechar; 70d disponiveis -> folga -10
    assert pj["dias_para_fechar"] == 80 and pj["folga_dias"] == -10, f"projecao (got {pj})"
    assert pj["ritmo_necessario"] == round(4000 / 70, 1), "ritmo necessario derivado"
    q = [b for b in r["blocos"] if b["tipo"] == "questoes"][0]
    assert q["qtd"] == int(dp.TEMPO_DEFAULT_H * dp.QUESTOES_POR_HORA *
                           dp.FATOR_ENERGIA[dp.ENERGIA_DEFAULT]), \
        "grade atrasada -> capacidade maxima do dia"


def test_descanso_energia_baixa_com_folga():
    s = dict(SINAIS_BASE, restante_grade_q=500, ritmo_real=40.0)  # 13d p/ fechar, folga 57
    r = dp.recomendar_dia(s, energia="baixa")
    tipos = _tipos(r)
    assert "descanso" in tipos, f"R2 dispara (got {tipos})"
    assert "questoes" not in tipos, "dia de descanso nao empilha tema novo"
    fsrs = [b for b in r["blocos"] if b["tipo"] == "fsrs"]
    assert fsrs and fsrs[0]["qtd"] <= dp.FSRS_LEVE_CAP, "FSRS leve capado"
    assert any("descanso" in j for j in r["justificativa"]), "justificativa nomeia o motivo"


def test_energia_baixa_sem_folga_nao_descansa():
    r = dp.recomendar_dia(dict(SINAIS_BASE), energia="baixa")  # folga -10
    assert "descanso" not in _tipos(r), "sem folga nao ha descanso mesmo com energia baixa"
    q = [b for b in r["blocos"] if b["tipo"] == "questoes"][0]
    esperado = int(dp.TEMPO_DEFAULT_H * dp.QUESTOES_POR_HORA * dp.FATOR_ENERGIA["baixa"])
    assert q["qtd"] == esperado, f"capacidade modulada pela energia (got {q['qtd']})"


def test_simulado_semana_multipla():
    s = dict(SINAIS_BASE, semana_conteudo=12)  # 12 % 4 == 0
    r = dp.recomendar_dia(s)
    assert "simulado" in _tipos(r), "R3: semana multipla dispara slot de simulado"


def test_tempo_curto_reduz_capacidade():
    r = dp.recomendar_dia(dict(SINAIS_BASE), tempo_h=1.0, energia="media")
    q = [b for b in r["blocos"] if b["tipo"] == "questoes"][0]
    assert q["qtd"] == int(1.0 * dp.QUESTOES_POR_HORA * dp.FATOR_ENERGIA["media"]), \
        f"tempo curto reduz o bloco (got {q['qtd']})"
    assert r["defaults_assumidos"] is False, "contexto informado -> sem defaults"


def test_frescos_viram_primeiro_bloco():
    s = dict(SINAIS_BASE, frescos_tema_alvo=[{"id": 730}, {"id": 729}])
    r = dp.recomendar_dia(s)
    assert r["blocos"][0]["tipo"] == "mini-drill", "R1: anti-reincidencia primeiro"
    assert r["blocos"][0]["qtd"] == 2, "qtd = numero de cards frescos"


def test_folga_positiva_limita_pelo_necessario():
    s = dict(SINAIS_BASE, restante_grade_q=700, ritmo_real=40.0)  # nec 10/dia; folga 52
    r = dp.recomendar_dia(s)
    q = [b for b in r["blocos"] if b["tipo"] == "questoes"][0]
    assert q["qtd"] == 10, f"sem atraso, alvo = ritmo necessario (got {q['qtd']})"


def test_paridade_contrato_cli():
    path = os.path.join(ROOT, "core", "contracts", "orquestracao-contract.md")
    with open(path, encoding="utf-8") as fh:
        texto = fh.read()
    params = re.findall(r"^\|\s*([A-Z_]+)\s*\|\s*([0-9.]+)\s*\|", texto, re.M)
    assert len(params) >= 7, f"tabela de parametros no contrato (got {len(params)})"
    for nome, valor in params:
        assert hasattr(dp, nome), f"constante {nome} do contrato ausente no CLI"
        v_cli = getattr(dp, nome)
        assert float(v_cli) == float(valor), \
            f"paridade {nome}: contrato={valor} CLI={v_cli}"


def test_render_inclui_recomendacao():
    p = {
        "data": "2026-07-06", "dormant": {"empty": True},
        "volume": {"total": 100, "acertos": 80, "hoje": 0, "mes": 0, "alvo_enamed": 12000,
                   "faltam": 11900, "dias_ate_marco": 70, "ritmo_alvo": 170.0},
        "fsrs": {"atrasados": 1, "hoje": 2, "backlog_novos": 10},
        "divida": {"atrasados": 1, "regime_divida": False, "teto_base": 30, "teto_efetivo": 30},
        "cronograma": None, "cronograma_hint": None, "sugestao_passo": "x",
        "recomendacao": dp.recomendar_dia(dict(SINAIS_BASE)),
    }
    out = dp.render(p)
    assert "Recomendação do dia" in out, "secao presente no render"
    assert "projeção" in out and "sinais:" in out, "projecao e sinais renderizados"
    assert "[defaults:" in out, "defaults declarados no output"


def _db_temp_minimo():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.executescript("""
        CREATE TABLE sessoes_bulk (id INTEGER PRIMARY KEY AUTOINCREMENT, sessao_num INTEGER,
            area TEXT, questoes_feitas INTEGER, questoes_acertadas INTEGER,
            data_sessao DATE, observacoes TEXT);
        CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY AUTOINCREMENT,
            area TEXT, tema TEXT);
        CREATE TABLE flashcards (id INTEGER PRIMARY KEY AUTOINCREMENT, questao_id INTEGER,
            tema_id INTEGER, tipo TEXT, frente_pergunta TEXT);
        CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER, due TIMESTAMP);
    """)
    con.commit()
    con.close()
    return path


def test_get_ritmo_real_janela():
    tmp = _db_temp_minimo()
    orig = db.DB_PATH
    db.DB_PATH = tmp
    try:
        con = sqlite3.connect(tmp)
        con.execute("INSERT INTO sessoes_bulk (sessao_num, area, questoes_feitas, "
                    "questoes_acertadas, data_sessao) VALUES "
                    "(1, 'Cirurgia', 60, 44, date('now', '-1 day')),"
                    "(2, 'Pediatria', 40, 30, date('now', '-5 day')),"
                    "(3, 'Simulado', 90, 60, date('now', '-2 day')),"     # Simulado nao conta
                    "(4, 'Cirurgia', 100, 70, date('now', '-30 day'))")   # fora da janela
        con.commit()
        con.close()
        assert db.get_ritmo_real(14) == round(100 / 14, 1), "soma so a janela, sem Simulado"
    finally:
        db.DB_PATH = orig
        os.remove(tmp)


def test_get_fresh_error_cards():
    tmp = _db_temp_minimo()
    orig = db.DB_PATH
    db.DB_PATH = tmp
    try:
        con = sqlite3.connect(tmp)
        con.execute("INSERT INTO taxonomia_cronograma (id, area, tema) VALUES "
                    "(1, 'Cirurgia', 'Apendicite Aguda'), (2, 'Pediatria', 'Imunizacoes')")
        con.execute("INSERT INTO flashcards (id, tema_id, tipo, frente_pergunta) VALUES "
                    "(730, 1, 'elo_quebrado', 'caso classico...'),"
                    "(500, 1, 'elo_quebrado', 'antigo...'),"
                    "(731, 2, 'elo_quebrado', 'outro tema...')")
        # 730/731 frescos (due=agora); 500 velho; todos state 0
        con.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES "
                    "(730, 0, datetime('now')), "
                    "(500, 0, datetime('now', '-10 day')), "
                    "(731, 0, datetime('now'))")
        con.commit()
        con.close()
        frescos = db.get_fresh_error_cards(tema="Apendicite", janela_horas=48)
        ids = sorted(c["id"] for c in frescos)
        assert ids == [730], f"so o fresco DO TEMA entra (got {ids})"
        todos = db.get_fresh_error_cards(janela_horas=48)
        assert sorted(c["id"] for c in todos) == [730, 731], "sem filtro: frescos de todos os temas"
    finally:
        db.DB_PATH = orig
        os.remove(tmp)


if __name__ == "__main__":
    fns = [test_mix_normal, test_descanso_energia_baixa_com_folga,
           test_energia_baixa_sem_folga_nao_descansa, test_simulado_semana_multipla,
           test_tempo_curto_reduz_capacidade, test_frescos_viram_primeiro_bloco,
           test_folga_positiva_limita_pelo_necessario, test_paridade_contrato_cli,
           test_render_inclui_recomendacao, test_get_ritmo_real_janela,
           test_get_fresh_error_cards]
    falhas = 0
    for fn in fns:
        try:
            fn()
            print("  OK  " + fn.__name__)
        except AssertionError as e:
            falhas += 1
            print("  XX  %s: %s" % (fn.__name__, e))
    print()
    if falhas:
        print("FALHOU: %d teste(s)" % falhas)
        sys.exit(1)
    print("TODOS OS TESTES PASSARAM (part-2)")
