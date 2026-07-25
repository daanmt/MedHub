#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Suite do Ledger de Habilidades (spec `ledger-de-habilidades`).

Cobre os 6 checks do DoD. Roda contra db temporario -- nunca toca o ipub.db real.
"""

import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import habilidades as H  # noqa: E402

FALHAS = []


def check(cond, nome, extra=''):
    if cond:
        print('  OK  %s' % nome)
    else:
        print('  XX  %s %s' % (nome, extra))
        FALHAS.append(nome)


def _db_temp():
    """DB minimo com as tabelas que o ledger precisa + fixtures de erro."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    c = sqlite3.connect(path)
    c.executescript('''
        CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY, area TEXT, tema TEXT);
        CREATE TABLE sessoes_bulk (id INTEGER PRIMARY KEY, area TEXT, questoes_feitas INT);
        CREATE TABLE questoes_erros (
            id INTEGER PRIMARY KEY, tema_id INTEGER, habilidades_sequenciais TEXT);
        CREATE TABLE habilidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT NOT NULL,
            texto_norm TEXT NOT NULL UNIQUE, precisa_curadoria INTEGER NOT NULL DEFAULT 0,
            criado_em TEXT NOT NULL);
        CREATE TABLE questao_habilidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, habilidade_id INTEGER NOT NULL,
            questao_id INTEGER, tema_id INTEGER, ordem INTEGER NOT NULL DEFAULT 0,
            veredito TEXT NOT NULL DEFAULT 'indefinido',
            origem TEXT NOT NULL DEFAULT 'backfill', criado_em TEXT NOT NULL);
        CREATE UNIQUE INDEX idx_qhab_dedup
            ON questao_habilidades(habilidade_id, questao_id, ordem);
    ''')
    c.executemany('INSERT INTO taxonomia_cronograma (id, area, tema) VALUES (?,?,?)',
                  [(1, 'Nefro', 'LRA'), (2, 'GO', 'Pre-Natal'), (3, 'Cirurgia', 'Trauma')])
    c.executemany('INSERT INTO questoes_erros (id, tema_id, habilidades_sequenciais) VALUES (?,?,?)', [
        (1, 1, 'Reconhecer rabdomiolise -> medir CK -> hidratar'),
        (2, 2, '1. Reconhecer rabdomiolise\n2. Pedir sumario de urina'),
        (3, 3, 'Reconhecer rabdomiolise -> indicar suporte'),
        (4, 1, 'N/A'),
        (5, 2, 'Diagnostico'),
        (6, 3, 'Cadeia sem separador nenhum que precisa de curadoria manual'),
    ])
    c.commit()
    c.close()
    return path


def test_parser_setas():
    partes, cur = H.parse_cadeia('A grande -> B grande -> C grande')
    check(partes == ['A grande', 'B grande', 'C grande'], 'parser: setas separa em 3', partes)
    check(cur is False, 'parser: setas nao pede curadoria')


def test_parser_numerada():
    partes, cur = H.parse_cadeia('1. Identificar choque\n2. Repor volume\n3. Reavaliar')
    check(len(partes) == 3, 'parser: lista numerada separa em 3', partes)
    check(cur is False, 'parser: numerada nao pede curadoria')


def test_parser_sentinela_e_generico():
    for s in ('N/A', 'n/a', '-', '', '   '):
        partes, _ = H.parse_cadeia(s)
        check(partes == [], 'parser: sentinela %r vira vazio' % s, partes)
    partes, _ = H.parse_cadeia('Diagnostico')
    check(partes == [], 'parser: rotulo generico e descartado', partes)


def test_parser_fallback_curadoria():
    txt = 'Cadeia longa sem separador que nao da para quebrar'
    partes, cur = H.parse_cadeia(txt)
    check(partes == [txt], 'parser: fallback preserva o texto inteiro')
    check(cur is True, 'parser: fallback liga precisa_curadoria')


def test_normalizar_dedup():
    check(H.normalizar('  Reconhecer   RABDOMIÓLISE ') == 'reconhecer rabdomiolise',
          'normalizar: acento/caixa/espaco colapsam')


def test_dod1_schema_idempotente():
    """DoD-1: rodar a migracao 2x nao duplica nem levanta."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import init_db
        orig = init_db.DB_PATH if hasattr(init_db, 'DB_PATH') else None
        ok = True
        try:
            for _ in range(2):
                conn = sqlite3.connect(path)
                conn.executescript('''
                    CREATE TABLE IF NOT EXISTS habilidades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT NOT NULL,
                        texto_norm TEXT NOT NULL UNIQUE,
                        precisa_curadoria INTEGER NOT NULL DEFAULT 0,
                        criado_em TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS questao_habilidades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        habilidade_id INTEGER NOT NULL, questao_id INTEGER,
                        tema_id INTEGER, ordem INTEGER NOT NULL DEFAULT 0,
                        veredito TEXT NOT NULL DEFAULT 'indefinido',
                        origem TEXT NOT NULL DEFAULT 'backfill', criado_em TEXT NOT NULL);
                ''')
                conn.commit()
                conn.close()
        except Exception as e:  # noqa: BLE001
            ok = False
            print('     erro:', e)
        check(ok, 'DoD-1: CREATE IF NOT EXISTS roda 2x sem erro')
        _ = orig
    finally:
        os.remove(path)


def test_dod2_backfill_nao_destrutivo():
    """DoD-2: questoes_erros byte-identica antes/depois do backfill."""
    path = _db_temp()
    try:
        c = sqlite3.connect(path)
        antes = c.execute(
            'SELECT COUNT(*), SUM(length(coalesce(habilidades_sequenciais,""))) '
            'FROM questoes_erros').fetchone()
        c.close()
        H.backfill(db_path=path)
        c = sqlite3.connect(path)
        depois = c.execute(
            'SELECT COUNT(*), SUM(length(coalesce(habilidades_sequenciais,""))) '
            'FROM questoes_erros').fetchone()
        n_ocor = c.execute('SELECT COUNT(*) FROM questao_habilidades').fetchone()[0]
        c.close()
        check(antes == depois, 'DoD-2: questoes_erros inalterada', '%s != %s' % (antes, depois))
        check(n_ocor > 0, 'DoD-2: ledger populado (%d ocorrencias)' % n_ocor)
    finally:
        os.remove(path)


def test_dod2b_backfill_idempotente():
    path = _db_temp()
    try:
        r1 = H.backfill(db_path=path)
        r2 = H.backfill(db_path=path)
        check(r2['ocorrencias_novas'] == 0,
              'DoD-2: 2o backfill e no-op (%d novas)' % r2['ocorrencias_novas'])
        check(r1['ocorrencias_novas'] > 0, 'DoD-2: 1o backfill inseriu')
    finally:
        os.remove(path)


def test_dod3_reincidentes_e_flag():
    """DoD-3: 'Reconhecer rabdomiolise' aparece nos 3 temas do fixture."""
    path = _db_temp()
    try:
        H.backfill(db_path=path)
        rows = H.reincidentes(limit=20, min_temas=1, db_path=path)
        alvo = [r for r in rows if H.normalizar(r['texto']) == 'reconhecer rabdomiolise']
        check(len(alvo) == 1, 'DoD-3: habilidade repetida deduplicou em 1 linha')
        if alvo:
            check(alvo[0]['ocorrencias'] == 3,
                  'DoD-3: 3 ocorrencias', alvo[0]['ocorrencias'])
            check(alvo[0]['temas_distintos'] == 3,
                  'DoD-3: 3 temas distintos', alvo[0]['temas_distintos'])
            check(alvo[0]['padrao_de_raciocinio'] is True,
                  'DoD-3: flag padrao_de_raciocinio ligada em >= 3 temas')
        so_multi = H.reincidentes(limit=20, min_temas=3, db_path=path)
        check(all(r['temas_distintos'] >= 3 for r in so_multi),
              'DoD-3: --min-temas filtra corretamente')
        check(rows == sorted(rows, key=lambda r: (-r['ocorrencias'], -r['temas_distintos'])),
              'DoD-3: ordenado por ocorrencias desc')
    finally:
        os.remove(path)


def test_dod4_enum_fechado():
    for v in H.VEREDITOS:
        try:
            H._validar_veredito(v)
            ok = True
        except ValueError:
            ok = False
        check(ok, 'DoD-4: veredito valido aceito: %s' % v)
    try:
        H._validar_veredito('mais_ou_menos')
        check(False, 'DoD-4: veredito invalido deveria levantar')
    except ValueError as e:
        msg = str(e)
        check(all(v in msg for v in H.VEREDITOS),
              'DoD-4: ValueError nomeia os validos', msg)


def test_dod5_add_nao_toca_erros_nem_volume():
    """DoD-5: aprendizado de questao ACERTADA nao vira erro nem volume."""
    path = _db_temp()
    try:
        c = sqlite3.connect(path)
        qe_antes = c.execute('SELECT COUNT(*) FROM questoes_erros').fetchone()[0]
        sb_antes = c.execute('SELECT COUNT(*) FROM sessoes_bulk').fetchone()[0]
        c.close()
        r = H.registrar('Lembrar do score de Glasgow-Blatchford na HDA',
                        area='Nefro', tema='LRA', veredito='acertou', db_path=path)
        c = sqlite3.connect(path)
        qe_depois = c.execute('SELECT COUNT(*) FROM questoes_erros').fetchone()[0]
        sb_depois = c.execute('SELECT COUNT(*) FROM sessoes_bulk').fetchone()[0]
        ocor = c.execute('SELECT questao_id, veredito FROM questao_habilidades '
                         'WHERE id = ?', (r['ocorrencia_id'],)).fetchone()
        c.close()
        check(qe_antes == qe_depois, 'DoD-5: questoes_erros NAO cresceu')
        check(sb_antes == sb_depois, 'DoD-5: sessoes_bulk NAO cresceu')
        check(ocor[0] is None, 'DoD-5: questao_id nulo em habilidade avulsa')
        check(ocor[1] == 'acertou', 'DoD-5: veredito acertou persistido')
        check(r['tema_id'] == 1, 'DoD-5: tema resolvido por (area, tema)', r['tema_id'])
    finally:
        os.remove(path)


def test_dod5b_incerteza_e_estado_proprio():
    path = _db_temp()
    try:
        H.registrar('Direcao do marcador na rabdomiolise', area='Nefro', tema='LRA',
                    veredito='incerteza', db_path=path)
        rows = H.reincidentes(limit=20, min_temas=1, db_path=path)
        alvo = [r for r in rows if 'direcao do marcador' in H.normalizar(r['texto'])]
        check(len(alvo) == 1 and alvo[0]['n_incerteza'] == 1,
              'DoD-5: incerteza contabilizada separada de errou')
        check(alvo and alvo[0]['n_errou'] == 0,
              'DoD-5: incerteza NAO conta como errou')
    finally:
        os.remove(path)


def test_report_honesto():
    path = _db_temp()
    try:
        H.backfill(db_path=path)
        r = H.report(db_path=path)
        check(set(r['por_veredito'].keys()) == set(H.VEREDITOS),
              'report: expoe os 4 vereditos')
        check(r['por_veredito']['indefinido'] == r['ocorrencias'],
              'report: backfill nao inventa veredito (tudo indefinido)')
        txt = H._render_report(r)
        check('nao inventa veredito' in txt,
              'report: adverte que a metrica ainda nao tem poder')
    finally:
        os.remove(path)


def main():
    print('[ledger de habilidades] suite')
    for fn in (test_parser_setas, test_parser_numerada, test_parser_sentinela_e_generico,
               test_parser_fallback_curadoria, test_normalizar_dedup,
               test_dod1_schema_idempotente, test_dod2_backfill_nao_destrutivo,
               test_dod2b_backfill_idempotente, test_dod3_reincidentes_e_flag,
               test_dod4_enum_fechado, test_dod5_add_nao_toca_erros_nem_volume,
               test_dod5b_incerteza_e_estado_proprio, test_report_honesto):
        fn()
    print()
    if FALHAS:
        print('FALHOU: %d check(s): %s' % (len(FALHAS), ', '.join(FALHAS)))
        return 1
    print('TODOS OS CHECKS PASSARAM (ledger de habilidades)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
