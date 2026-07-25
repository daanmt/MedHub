#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Suite do Diagnostico de Variancia e Zona (spec `variancia-e-zona`).

Cobre os 6 checks do DoD. Fixtures deterministicas, db temporario.
"""

import os
import sqlite3
import statistics
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import variancia as V  # noqa: E402

FALHAS = []


def check(cond, nome, extra=''):
    if cond:
        print('  OK  %s' % nome)
    else:
        print('  XX  %s %s' % (nome, extra))
        FALHAS.append(nome)


def _db(blocos, simulados=()):
    """blocos: lista de (data, feitas, acertos). simulados: lista de datas."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    c = sqlite3.connect(path)
    c.executescript('''
        CREATE TABLE sessoes_bulk (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sessao_num INTEGER, area TEXT,
            questoes_feitas INTEGER, questoes_acertadas INTEGER, data_sessao DATE,
            observacoes TEXT);
        CREATE TABLE preparacao_estado (
            chave TEXT PRIMARY KEY, valor TEXT NOT NULL,
            atualizado_em TEXT, fonte TEXT);
    ''')
    c.executemany('INSERT INTO sessoes_bulk (area, questoes_feitas, questoes_acertadas, '
                  'data_sessao) VALUES (?,?,?,?)',
                  [('Clinica', f, a, d) for d, f, a in blocos])
    for d in simulados:
        c.execute('INSERT INTO sessoes_bulk (area, questoes_feitas, questoes_acertadas, '
                  "data_sessao) VALUES ('Simulado', 100, 70, ?)", (d,))
    c.commit()
    c.close()
    return path


def test_dod1_metricas_estatistica():
    """Desvio populacional sobre serie conhecida."""
    blocos = [('2026-01-0%d' % i, 100, v) for i, v in enumerate([60, 70, 80, 90], 1)]
    path = _db(blocos)
    try:
        m = V.metricas(db_path=path)
        esperado = statistics.pstdev([60.0, 70.0, 80.0, 90.0])
        check(m['n'] == 4, 'DoD-1: n de blocos', m['n'])
        check(m['media'] == 75.0, 'DoD-1: media', m['media'])
        check(abs(m['desvio'] - round(esperado, 1)) < 0.05,
              'DoD-1: desvio POPULACIONAL (%.2f)' % esperado, m['desvio'])
        check(m['amplitude'] == 30.0, 'DoD-1: amplitude', m['amplitude'])
        check(m['coef_variacao'] == round(esperado / 75 * 100, 1),
              'DoD-1: coeficiente de variacao', m['coef_variacao'])
    finally:
        os.remove(path)


def test_dod1_piso_filtra_ruido():
    """Bloco abaixo do piso nao entra -- 5q gera % de granularidade 20 pp."""
    path = _db([('2026-01-01', 100, 80), ('2026-01-02', 5, 1),
                ('2026-01-03', 100, 80)])
    try:
        m = V.metricas(db_path=path, piso=15)
        check(m['n'] == 2, 'DoD-1: piso exclui bloco de 5q', m['n'])
        check(m['desvio'] == 0.0, 'DoD-1: sem o ruido, desvio zera', m['desvio'])
        m2 = V.metricas(db_path=path, piso=1)
        check(m2['n'] == 3, 'DoD-1: piso configuravel deixa entrar', m2['n'])
    finally:
        os.remove(path)


def test_dod1_janela_ultimos():
    path = _db([('2026-01-0%d' % i, 100, v)
                for i, v in enumerate([10, 20, 90, 90], 1)])
    try:
        m = V.metricas(db_path=path, ultimos=2)
        check(m['n'] == 2 and m['media'] == 90.0,
              'DoD-1: --ultimos limita a janela', (m['n'], m['media']))
    finally:
        os.remove(path)


def test_dod1_serie_curta():
    path = _db([('2026-01-01', 100, 80)])
    try:
        m = V.metricas(db_path=path)
        check(m['insuficiente'] is True, 'DoD-1: 1 bloco -> insuficiente')
    finally:
        os.remove(path)


def test_dod2_quatro_quadrantes():
    """Zona de 2 eixos: os 4 quadrantes + os nomes exatos."""
    casos = [
        (60.0, 40.0, 'CONTEUDO'),
        (80.0, 40.0, 'COBERTURA'),
        (60.0, 90.0, 'RETENCAO'),
        (80.0, 90.0, 'DIRECIONAMENTO'),
    ]
    for media, cob, esperado in casos:
        nome, presc, ed, ec = V.classificar(media, cob)
        check(nome == esperado,
              'DoD-2: (%.0f%%, %.0f%%) -> %s' % (media, cob, esperado), nome)
        check(bool(presc), 'DoD-2: %s vem com prescricao' % esperado)


def test_dod2_cortes_nos_limites():
    check(V.classificar(70.0, 70.0)[0] == 'DIRECIONAMENTO',
          'DoD-2: corte e >= (70/70 = alto/alta)')
    check(V.classificar(69.9, 69.9)[0] == 'CONTEUDO',
          'DoD-2: logo abaixo do corte = baixo/baixa')
    check(V.classificar(None, 50)[0] is None, 'DoD-2: media None -> zona None')
    check(V.classificar(80, None)[0] is None, 'DoD-2: cobertura None -> zona None')


def test_dod2_cobertura_nao_usa_campo_inflado():
    """A cobertura NAO pode vir de taxonomia_cronograma.questoes_realizadas.

    Esse campo esta inflado (~19.6k contra 5.2k reais) e classificaria como
    'cobertura alta' quem ainda tem 4.263 questoes de grade pela frente.
    """
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'variancia.py'), encoding='utf-8').read()
    corpo = src.split('def get_cobertura')[1].split('\ndef ')[0]
    check('questoes_realizadas' not in corpo.replace('questoes_realizadas`', ''),
          'DoD-2: get_cobertura nao consulta questoes_realizadas')
    check('grade' in corpo and 'semana_conteudo' in corpo,
          'DoD-2: cobertura derivada da grade + semana de conteudo')


def test_dod2_cobertura_degrada():
    path = _db([('2026-01-01', 100, 80), ('2026-01-02', 100, 80)])
    try:
        cob = V.get_cobertura(db_path=path, grade={'semanas': []})
        check(cob['pct'] is None, 'DoD-2: grade vazia -> pct None (nao mente)')
        z = V.zona(db_path=path)
        check(z['zona'] is None or isinstance(z['zona'], str),
              'DoD-2: zona nao levanta com dados parciais')
    finally:
        os.remove(path)


def test_dod3_variancia_e_sinal_independente():
    """Desvio >= 10 pp aciona simulado em QUALQUER zona."""
    alta = [('2026-01-0%d' % i, 100, v) for i, v in enumerate([50, 90, 55, 95], 1)]
    path = _db(alta)
    try:
        m = V.metricas(db_path=path)
        check(m['desvio'] >= V.DESVIO_ALERTA_PP, 'DoD-3: serie dispersa -> desvio alto',
              m['desvio'])
        check(m['variancia_alta'] is True, 'DoD-3: flag variancia_alta ligada')
    finally:
        os.remove(path)
    baixa = [('2026-01-0%d' % i, 100, v) for i, v in enumerate([78, 80, 79, 81], 1)]
    path = _db(baixa)
    try:
        m = V.metricas(db_path=path)
        check(m['variancia_alta'] is False, 'DoD-3: serie estavel -> flag desligada',
              m['desvio'])
    finally:
        os.remove(path)


def test_dod4_simulado_check():
    path = _db([('2026-01-01', 100, 80)], simulados=[])
    try:
        s = V.simulado_check(db_path=path)
        check(s['em_debito'] is True, 'DoD-4: sem simulado -> em debito')
        check(s['ultimo'] is None, 'DoD-4: ultimo None quando nunca houve')
    finally:
        os.remove(path)
    path = _db([('2026-01-01', 100, 80)], simulados=["date('now')"])
    try:
        c = sqlite3.connect(path)
        c.execute("UPDATE sessoes_bulk SET data_sessao = date('now') "
                  "WHERE area = 'Simulado'")
        c.commit(); c.close()
        s = V.simulado_check(db_path=path)
        check(s['em_debito'] is False, 'DoD-4: simulado na janela -> sem debito')
        check(s['na_janela'] == 1, 'DoD-4: conta o simulado da janela', s['na_janela'])
    finally:
        os.remove(path)


def test_dod4_simulado_nao_entra_na_serie():
    """Simulado tem serie propria -- nao polui a variancia dos blocos tematicos."""
    path = _db([('2026-01-01', 100, 80), ('2026-01-02', 100, 80)],
               simulados=['2026-01-03'])
    try:
        serie = V.get_serie(db_path=path)
        check(len(serie) == 2, 'DoD-4: simulado fora da serie de blocos', len(serie))
    finally:
        os.remove(path)


def test_dod5_render_nao_levanta():
    path = _db([('2026-01-0%d' % i, 100, v) for i, v in enumerate([50, 90, 60, 85], 1)])
    try:
        z = V.zona(db_path=path)
        s = V.simulado_check(db_path=path)
        txt = V._render(z, s)
        check(isinstance(txt, str) and len(txt) > 20, 'DoD-5: render produz texto')
    finally:
        os.remove(path)


def main():
    print('[variancia e zona] suite')
    for fn in (test_dod1_metricas_estatistica, test_dod1_piso_filtra_ruido,
               test_dod1_janela_ultimos, test_dod1_serie_curta,
               test_dod2_quatro_quadrantes, test_dod2_cortes_nos_limites,
               test_dod2_cobertura_nao_usa_campo_inflado, test_dod2_cobertura_degrada,
               test_dod3_variancia_e_sinal_independente, test_dod4_simulado_check,
               test_dod4_simulado_nao_entra_na_serie, test_dod5_render_nao_levanta):
        fn()
    print()
    if FALHAS:
        print('FALHOU: %d check(s): %s' % (len(FALHAS), ', '.join(FALHAS)))
        return 1
    print('TODOS OS CHECKS PASSARAM (variancia e zona)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
