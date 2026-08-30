#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ledger de Habilidades -- CLI standalone (spec `ledger-de-habilidades`).

Promove `questoes_erros.habilidades_sequenciais` (prosa "A -> B -> C") a
entidade consultavel, respondendo a pergunta que o plato dos 75-80% exige:
*quais habilidades eu falho repetidamente, atraves de temas diferentes?*

Fronteira dura: este CLI **nunca** escreve em `questoes_erros`, `sessoes_bulk`,
`flashcards`, `fsrs_cards` ou `fsrs_revlog`. Escreve apenas em `habilidades` e
`questao_habilidades`. O campo de prosa de origem permanece intacto.

Uso:
    python tools/habilidades.py --backfill [--dry-run]
    python tools/habilidades.py --report
    python tools/habilidades.py --reincidentes [--limit N] [--min-temas N]
    python tools/habilidades.py --add "texto" --area AREA --tema TEMA \
                                [--veredito errou|acertou|incerteza|indefinido]

`import sqlite3` aqui e autorizado: CLI standalone em tools/ (ver
`.vibeflow/patterns/db-access-layer.md` e conventions.md).
"""

import argparse
import os
import re
import sqlite3
import sys
import unicodedata
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ipub.db')

# Enum fechado. Ordem = severidade crescente para efeito de relatorio.
VEREDITOS = ('acertou', 'incerteza', 'desatencao', 'errou', 'indefinido')

# Separador canonico da cadeia. Garantido pela convencao ASCII do AGENTE.md
# secao 4.5 (Zero LaTeX / zero setas Unicode) -- a prosa legada usa " -> ".
SEP = '->'

# Segundo formato encontrado no backfill real: lista NUMERADA multi-linha
# ("1. Identificar X\n2. Reconhecer Y"). Responde por ~22% dos registros
# historicos. Ignorar isso jogaria 130 cadeias inteiras na fila de curadoria.
RE_NUMERADA = re.compile(r'(?:^|\n)\s*\d+[\.\)]\s+')

# Sentinelas: valores que ocupam o campo mas NAO sao habilidade. Sem este
# filtro, "N/A" vira a habilidade mais reincidente do ledger (125 ocorrencias
# em 31 temas no backfill real) e a metrica inteira vira teatro.
SENTINELAS = {'', 'n/a', 'na', 'nao se aplica', '-', '--', 'none', 'null', 'sem'}

# Fragmentos genericos demais para servirem de habilidade. Sao rotulos de
# categoria ("Diagnostico", "Terapeutica"), nao elos de raciocinio: agregar por
# eles nao aponta nada acionavel.
GENERICOS = {'diagnostico', 'terapeutica', 'conduta', 'tratamento',
             'clinica', 'epidemiologia', 'fisiopatologia'}

# Tabelas que este CLI tem permissao de escrever. Qualquer outra e defeito.
TABELAS_ESCRITA = ('habilidades', 'questao_habilidades')


def normalizar(texto):
    """Chave de dedup: minusculas, sem acento, espacos colapsados.

    Deliberadamente simples -- sem stemming nem fuzzy. Falso-merge e pior que
    duplicata (decisao tecnica do spec): duas grafias distintas viram duas
    linhas, e a curadoria decide depois. Nunca o contrario.
    """
    if texto is None:
        return ''
    s = unicodedata.normalize('NFKD', str(texto))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return ' '.join(s.lower().split())


def _util(texto):
    """Um fragmento so vira habilidade se carregar informacao acionavel."""
    n = normalizar(texto)
    return bool(n) and n not in SENTINELAS and n not in GENERICOS and len(n) > 3


def parse_cadeia(prosa):
    """Quebra a cadeia de raciocinio numa lista de habilidades.

    Reconhece DOIS formatos, nesta ordem: (1) setas "A -> B -> C"; (2) lista
    numerada multi-linha "1. A\\n2. B". Ambos aparecem no historico real.

    Retorna (lista_de_textos, precisa_curadoria). Registro que nao separa por
    nenhum dos dois NAO e descartado: vira uma unica habilidade com o texto
    inteiro e a flag ligada, para nao perder sinal silenciosamente. Sentinelas
    ("N/A") e rotulos genericos ("Diagnostico") sao filtrados -- eles nao sao
    habilidades e envenenariam a metrica de reincidencia.
    """
    if not prosa or not str(prosa).strip():
        return [], False
    bruto = str(prosa).strip()

    if SEP in bruto:
        partes = [p.strip() for p in bruto.split(SEP)]
        partes = [p for p in partes if _util(p)]
        if len(partes) >= 2:
            return partes, False
        return (partes, False) if partes else ([], False)

    if RE_NUMERADA.search(bruto):
        partes = [p.strip() for p in RE_NUMERADA.split(bruto)]
        partes = [p for p in partes if _util(p)]
        if len(partes) >= 2:
            return partes, False
        return (partes, False) if partes else ([], False)

    if not _util(bruto):
        return [], False
    return [bruto], True


def _validar_veredito(v):
    if v not in VEREDITOS:
        raise ValueError(
            "veredito invalido: %r -- validos: %s" % (v, ', '.join(VEREDITOS)))
    return v


def _conn(db_path=None):
    return sqlite3.connect(db_path or DB_PATH)


def _upsert_habilidade(cur, texto, precisa_curadoria, agora):
    """Insere no catalogo se nova; devolve o id em qualquer caso."""
    norm = normalizar(texto)
    if not norm:
        return None
    row = cur.execute(
        'SELECT id FROM habilidades WHERE texto_norm = ?', (norm,)).fetchone()
    if row:
        return row[0]
    cur.execute(
        'INSERT INTO habilidades (texto, texto_norm, precisa_curadoria, criado_em) '
        'VALUES (?, ?, ?, ?)',
        (texto.strip(), norm, 1 if precisa_curadoria else 0, agora))
    return cur.lastrowid


def backfill(db_path=None, dry_run=False):
    """Popula o ledger a partir dos registros existentes de `questoes_erros`.

    🔴 Somente-leitura sobre `questoes_erros`. Idempotente: o UNIQUE INDEX
    (habilidade_id, questao_id, ordem) faz reexecucao ser no-op.

    Veredito = 'indefinido' por design. Os registros historicos sao de questao
    errada, mas tipicamente quebra-se em UMA habilidade da cadeia, nao em todas.
    Marcar a cadeia inteira como 'errou' envenenaria a metrica de reincidencia,
    que e o produto. Curadoria incremental corrige depois.
    """
    conn = _conn(db_path)
    cur = conn.cursor()
    agora = datetime.now().isoformat(timespec='seconds')
    linhas = cur.execute(
        'SELECT id, tema_id, habilidades_sequenciais FROM questoes_erros '
        'ORDER BY id').fetchall()

    novas_hab = 0
    novas_ocor = 0
    curadoria = 0
    sem_cadeia = 0
    for questao_id, tema_id, prosa in linhas:
        partes, precisa = parse_cadeia(prosa)
        if not partes:
            sem_cadeia += 1
            continue
        if precisa:
            curadoria += 1
        for ordem, texto in enumerate(partes):
            antes = cur.execute('SELECT COUNT(*) FROM habilidades').fetchone()[0]
            hid = _upsert_habilidade(cur, texto, precisa, agora)
            if hid is None:
                continue
            if cur.execute('SELECT COUNT(*) FROM habilidades').fetchone()[0] > antes:
                novas_hab += 1
            try:
                cur.execute(
                    'INSERT INTO questao_habilidades '
                    '(habilidade_id, questao_id, tema_id, ordem, veredito, origem, criado_em) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (hid, questao_id, tema_id, ordem, 'indefinido', 'backfill', agora))
                novas_ocor += 1
            except sqlite3.IntegrityError:
                pass  # ja existe (reexecucao) -- idempotente por design

    if dry_run:
        conn.rollback()
    else:
        conn.commit()
    conn.close()
    return {
        'questoes_lidas': len(linhas),
        'habilidades_novas': novas_hab,
        'ocorrencias_novas': novas_ocor,
        'questoes_p_curadoria': curadoria,
        'questoes_sem_cadeia': sem_cadeia,
        'dry_run': dry_run,
    }


def registrar(texto, area=None, tema=None, veredito='errou', questao_id=None,
              origem='manual', db_path=None):
    """Registra uma habilidade avulsa -- inclusive de questao ACERTADA.

    🔴 Nao cria linha em `questoes_erros` nem em `sessoes_bulk`: aprendizado
    colhido de questao certa nao e erro e nao e volume. E o caminho para os
    'aprendizados nao-alvo' (a questao que voce acertou mas ensinou 3 coisas).
    """
    _validar_veredito(veredito)
    if not texto or not str(texto).strip():
        raise ValueError('texto da habilidade vazio')
    conn = _conn(db_path)
    cur = conn.cursor()
    agora = datetime.now().isoformat(timespec='seconds')

    tema_id = None
    if area and tema:
        row = cur.execute(
            'SELECT id FROM taxonomia_cronograma WHERE area = ? AND tema = ?',
            (area, tema)).fetchone()
        tema_id = row[0] if row else None

    hid = _upsert_habilidade(cur, texto, False, agora)
    cur.execute(
        'INSERT INTO questao_habilidades '
        '(habilidade_id, questao_id, tema_id, ordem, veredito, origem, criado_em) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        (hid, questao_id, tema_id, 0, veredito, origem, agora))
    ocor_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {'habilidade_id': hid, 'ocorrencia_id': ocor_id,
            'tema_id': tema_id, 'veredito': veredito}


def _avisar_f38(veredito, questao_id):
    """F38 (AUDITORIA_MEDHUB): `--add` COMPLEMENTA `insert_questao.py`, nao substitui.

    O pipeline de analise tem dois finais e a s127 provou que da para tomar um
    pelo outro: 6 erros analisados em profundidade, 7 habilidades gravadas aqui
    e ZERO linhas em `questoes_erros`. Os cards nasceram sem ancora
    (`questao_id=NULL`) e o substrato canonico (tipo_erro, alternativa marcada,
    explicacao correta) ficou so em prosa no log da sessao.

    Escreve em stderr de proposito: stdout desta CLI e consumido por script.
    """
    if veredito == 'errou' and questao_id is None:
        print("[WARN] F38: habilidade de veredito='errou' gravada SEM questao_id. "
              "Se este erro veio de uma questao de bloco, ele ainda precisa de "
              "linha propria em questoes_erros -- rode tools/insert_questao.py. "
              "Esta CLI complementa aquela, nunca a substitui "
              "(AUDITORIA_MEDHUB.md F38).", file=sys.stderr)


def reincidentes(limit=10, min_temas=1, db_path=None):
    """Habilidades ordenadas por dor: nº de ocorrencias e nº de temas DISTINTOS.

    `temas_distintos >= 3` e o sinal que separa **padrao de raciocinio** de
    **lacuna de conteudo**: falhar a mesma habilidade em 3 temas diferentes nao
    e nao saber o tema, e nao saber a habilidade.
    """
    conn = _conn(db_path)
    rows = conn.execute(
        'SELECT h.id, h.texto, '
        '       COUNT(qh.id)                AS ocorrencias, '
        '       COUNT(DISTINCT qh.tema_id)  AS temas_distintos, '
        "       SUM(CASE WHEN qh.veredito = 'errou'     THEN 1 ELSE 0 END) AS n_errou, "
        "       SUM(CASE WHEN qh.veredito = 'incerteza' THEN 1 ELSE 0 END) AS n_incerteza, "
        "       SUM(CASE WHEN qh.veredito = 'desatencao' THEN 1 ELSE 0 END) AS n_desatencao, "
        '       MAX(qh.criado_em)           AS ultima '
        '  FROM habilidades h '
        '  JOIN questao_habilidades qh ON qh.habilidade_id = h.id '
        ' GROUP BY h.id, h.texto '
        'HAVING temas_distintos >= ? '
        ' ORDER BY ocorrencias DESC, temas_distintos DESC '
        ' LIMIT ?', (min_temas, limit)).fetchall()
    conn.close()
    out = []
    for hid, texto, ocor, temas, n_err, n_inc, n_des, ultima in rows:
        out.append({
            'habilidade_id': hid, 'texto': texto, 'ocorrencias': ocor,
            'temas_distintos': temas, 'n_errou': n_err or 0,
            'n_incerteza': n_inc or 0, 'n_desatencao': n_des or 0, 'ultima': ultima,
            # o sinal que o video 1 chama de "sensibilidade a linhas de
            # raciocinio especificas", em oposicao a falta de conteudo
            'padrao_de_raciocinio': temas >= 3,
        })
    return out


def report(db_path=None):
    """Panorama honesto do ledger, incluindo o que ainda aguarda curadoria."""
    conn = _conn(db_path)
    cur = conn.cursor()
    total_hab = cur.execute('SELECT COUNT(*) FROM habilidades').fetchone()[0]
    total_ocor = cur.execute('SELECT COUNT(*) FROM questao_habilidades').fetchone()[0]
    curadoria = cur.execute(
        'SELECT COUNT(*) FROM habilidades WHERE precisa_curadoria = 1').fetchone()[0]
    por_veredito = dict(cur.execute(
        'SELECT veredito, COUNT(*) FROM questao_habilidades GROUP BY veredito').fetchall())
    multi = cur.execute(
        'SELECT COUNT(*) FROM (SELECT habilidade_id FROM questao_habilidades '
        ' GROUP BY habilidade_id HAVING COUNT(DISTINCT tema_id) >= 3)').fetchone()[0]
    conn.close()
    return {
        'habilidades_catalogadas': total_hab,
        'ocorrencias': total_ocor,
        'habilidades_p_curadoria': curadoria,
        'por_veredito': {v: por_veredito.get(v, 0) for v in VEREDITOS},
        'em_3_ou_mais_temas': multi,
    }


def _render_report(r):
    linhas = ['# Ledger de Habilidades -- panorama', '']
    linhas.append('- Habilidades catalogadas: %d' % r['habilidades_catalogadas'])
    linhas.append('- Ocorrencias registradas: %d' % r['ocorrencias'])
    linhas.append('- Em 3+ temas distintos (padrao de raciocinio): %d' % r['em_3_ou_mais_temas'])
    linhas.append('- Habilidades aguardando curadoria (cadeia nao separavel): %d' % r['habilidades_p_curadoria'])
    linhas.append('')
    linhas.append('## Por veredito')
    for v in VEREDITOS:
        linhas.append('- %-11s %d' % (v + ':', r['por_veredito'][v]))
    indef = r['por_veredito']['indefinido']
    if indef and indef == r['ocorrencias']:
        linhas.append('')
        linhas.append('⚠️  Todas as ocorrencias estao "indefinido" -- o backfill nao inventa '
                      'veredito. A metrica de reincidencia so ganha poder conforme a '
                      'curadoria marcar qual elo da cadeia de fato quebrou.')
    return '\n'.join(linhas)


def _render_reincidentes(rows, min_temas):
    if not rows:
        return ('Nenhuma habilidade com >= %d tema(s) distinto(s). '
                'Rode --backfill primeiro, ou baixe --min-temas.' % min_temas)
    linhas = ['# Habilidades reincidentes', '']
    for i, r in enumerate(rows, 1):
        flag = ' 🔴 PADRAO DE RACIOCINIO' if r['padrao_de_raciocinio'] else ''
        linhas.append('%2d. %s%s' % (i, r['texto'], flag))
        linhas.append('    ocorrencias %d | temas distintos %d | errou %d | incerteza %d'
                      % (r['ocorrencias'], r['temas_distintos'],
                         r['n_errou'], r['n_incerteza']))
    return '\n'.join(linhas)


def main(argv=None):
    p = argparse.ArgumentParser(description='Ledger de Habilidades (MedHub)')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--backfill', action='store_true',
                   help='popula o ledger a partir de questoes_erros (read-only na origem)')
    g.add_argument('--report', action='store_true', help='panorama do ledger')
    g.add_argument('--reincidentes', action='store_true',
                   help='habilidades por reincidencia e nº de temas distintos')
    g.add_argument('--add', metavar='TEXTO',
                   help='registra habilidade avulsa (serve p/ questao ACERTADA)')
    p.add_argument('--dry-run', action='store_true', help='backfill sem commit')
    p.add_argument('--limit', type=int, default=10)
    p.add_argument('--min-temas', type=int, default=1)
    p.add_argument('--area')
    p.add_argument('--tema')
    p.add_argument('--questao-id', type=int)
    p.add_argument('--veredito', default='errou', choices=list(VEREDITOS))
    args = p.parse_args(argv)

    if args.backfill:
        r = backfill(dry_run=args.dry_run)
        print('Backfill%s: %d questoes lidas | +%d habilidades | +%d ocorrencias | '
              '%d questoes p/ curadoria | %d questoes sem cadeia'
              % (' (DRY-RUN, sem commit)' if r['dry_run'] else '',
                 r['questoes_lidas'], r['habilidades_novas'], r['ocorrencias_novas'],
                 r['questoes_p_curadoria'], r['questoes_sem_cadeia']))
        return 0
    if args.report:
        print(_render_report(report()))
        return 0
    if args.reincidentes:
        print(_render_reincidentes(
            reincidentes(limit=args.limit, min_temas=args.min_temas), args.min_temas))
        return 0
    if args.add:
        r = registrar(args.add, area=args.area, tema=args.tema,
                      veredito=args.veredito, questao_id=args.questao_id)
        print('Registrado: habilidade #%d (ocorrencia #%d, veredito=%s, tema_id=%s)'
              % (r['habilidade_id'], r['ocorrencia_id'], r['veredito'], r['tema_id']))
        _avisar_f38(r['veredito'], args.questao_id)
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
