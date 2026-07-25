#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostico de Variancia e Zona -- CLI standalone (spec `variancia-e-zona`).

Troca a metrica que dirige o estudo: de MEDIA (que no plato ja esta boa e nao
diz o que fazer) para VARIANCIA entre blocos + uma ZONA de dois eixos que
prescreve o proximo movimento.

Tese de origem (Pedro Martins, 5 primeiros lugares): no plato dos 75-80%, nota
alta numa prova e nota baixa em outra mostra desempenho dependente do PERFIL DA
PROVA, nao do conhecimento. A media esconde isso; o desvio-padrao expoe.

Read-only sobre o `ipub.db`. Nao escreve em lugar nenhum.

Uso:
    python tools/variancia.py --metricas [--ultimos N] [--piso Q]
    python tools/variancia.py --zona
    python tools/variancia.py --simulado-check
    python tools/variancia.py --json

`import sqlite3` autorizado: CLI standalone em tools/ (db-access-layer.md).
"""

import argparse
import json
import os
import sqlite3
import statistics
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ipub.db')

# Piso de questoes por bloco. Bloco de 5q produz % com granularidade de 20 pp e
# envenena a variancia com ruido de amostragem, nao com sinal real.
PISO_QUESTOES = 15

# Corte de variancia. Acima disso, o desempenho depende do perfil da prova o
# suficiente para que MAIS BLOCO TEMATICO nao resolva -- so prova inteira e
# diversa (simulado) corrige.
DESVIO_ALERTA_PP = 10.0

# Cortes da zona. Fixos e grosseiros de proposito: auditaveis e testaveis.
CORTE_DESEMPENHO = 70.0   # %
CORTE_COBERTURA = 70.0    # % dos temas da grade com volume registrado

# Cadencia decidida na s126: 1 simulado/semana, contando no bloco dedicado.
JANELA_SIMULADO_DIAS = 7

ZONAS = {
    ('baixo', 'baixa'): (
        'CONTEUDO',
        'Falta base. Prioridade e volume de teoria + questoes por tema; '
        'flashcard e refinamento vem depois.'),
    ('alto', 'baixa'): (
        'COBERTURA',
        'Voce acerta o que estudou -- falta terreno. Prioridade e AVANCAR a grade; '
        'nao trocar cobertura por refinamento ainda.'),
    ('baixo', 'alta'): (
        'RETENCAO',
        'Voce ja passou pelo conteudo e nao reteve. Prioridade e FSRS/revisao '
        'direcionada, nao material novo.'),
    ('alto', 'alta'): (
        'DIRECIONAMENTO',
        'Conteudo coberto e desempenho bom. O gargalo e execucao e nuance: '
        'habilidade reincidente e simulado, nao mais tema.'),
}


def _conn(db_path=None):
    return sqlite3.connect(db_path or DB_PATH)


def get_serie(db_path=None, piso=PISO_QUESTOES, ultimos=None):
    """Serie de % de acerto por bloco (exclui simulado -- ele tem serie propria)."""
    conn = _conn(db_path)
    rows = conn.execute(
        "SELECT data_sessao, questoes_feitas, questoes_acertadas "
        "FROM sessoes_bulk "
        "WHERE area <> 'Simulado' AND questoes_feitas >= ? "
        "ORDER BY data_sessao, id", (int(piso),)).fetchall()
    conn.close()
    serie = [{'data': d, 'feitas': f, 'acertos': a, 'pct': round(a / f * 100, 1)}
             for d, f, a in rows if f]
    if ultimos:
        serie = serie[-int(ultimos):]
    return serie


def metricas(db_path=None, piso=PISO_QUESTOES, ultimos=None):
    """Media, desvio, amplitude e coeficiente de variacao da serie de blocos."""
    serie = get_serie(db_path, piso=piso, ultimos=ultimos)
    pcts = [b['pct'] for b in serie]
    if len(pcts) < 2:
        return {'n': len(pcts), 'insuficiente': True, 'serie': serie}
    media = statistics.mean(pcts)
    # populacional: os blocos sao a serie inteira, nao amostra de algo maior
    desvio = statistics.pstdev(pcts)
    return {
        'n': len(pcts),
        'insuficiente': False,
        'media': round(media, 1),
        'desvio': round(desvio, 1),
        'minimo': min(pcts),
        'maximo': max(pcts),
        'amplitude': round(max(pcts) - min(pcts), 1),
        'coef_variacao': round(desvio / media * 100, 1) if media else None,
        'variancia_alta': desvio >= DESVIO_ALERTA_PP,
        'serie': serie,
    }


def get_cobertura(db_path=None, grade=None):
    """% da GRADE percorrida = 1 - (questoes restantes / total da grade).

    🔴 Fonte deliberadamente NAO e `taxonomia_cronograma.questoes_realizadas`.
    Esse campo esta inflado (~19.6k contra 5.2k reais em `sessoes_bulk`, medido
    em 2026-07-25) e usa-lo classificaria como "cobertura alta" quem ainda tem
    4.263 questoes de grade pela frente. A grade (`core/cronograma/grade.json`)
    e versionada e o restante e derivado da semana de conteudo -- ambos audiveis.

    Degrada graciosamente: sem grade, devolve pct=None e a zona fica indefinida
    em vez de mentir.
    """
    try:
        if grade is None:
            import cronograma as cr
            grade = cr.load_grade()
        total_q = sum(s['total_questoes'] for s in grade['semanas'])
        conn = _conn(db_path)
        row = conn.execute(
            "SELECT valor FROM preparacao_estado WHERE chave = 'semana_conteudo'").fetchone()
        conn.close()
        semana = int(row[0]) if row and row[0] else None
        if not semana or not total_q:
            return {'total_grade_q': total_q or 0, 'restante_q': None, 'pct': None}
        restante = sum(s['total_questoes'] for s in grade['semanas']
                       if s['semana'] >= semana)
        pct = round((total_q - restante) / total_q * 100, 1)
        return {'total_grade_q': total_q, 'restante_q': restante,
                'semana_conteudo': semana, 'pct': pct}
    except Exception:
        return {'total_grade_q': 0, 'restante_q': None, 'pct': None}


def classificar(media_pct, cobertura_pct):
    """Funcao PURA de classificacao -- sem db, testavel por fixture.

    Devolve (nome_da_zona, prescricao, eixo_desempenho, eixo_cobertura).
    """
    if media_pct is None or cobertura_pct is None:
        return None, None, None, None
    eixo_d = 'alto' if media_pct >= CORTE_DESEMPENHO else 'baixo'
    eixo_c = 'alta' if cobertura_pct >= CORTE_COBERTURA else 'baixa'
    nome, prescricao = ZONAS[(eixo_d, eixo_c)]
    return nome, prescricao, eixo_d, eixo_c


def zona(db_path=None, piso=PISO_QUESTOES, ultimos=None):
    """Zona de DOIS eixos: desempenho x cobertura.

    O modelo de 1 eixo do video 1 (60-65% = conteudo, 70-80% = direcionamento)
    assume conteudo coberto -- e misclassifica quem tem nota de plato SEM ter
    fechado a grade. O segundo eixo separa 'nao sei' de 'ainda nao vi'.
    """
    m = metricas(db_path, piso=piso, ultimos=ultimos)
    cob = get_cobertura(db_path)
    if m.get('insuficiente') or cob['pct'] is None:
        return {'zona': None, 'motivo': 'dados insuficientes',
                'metricas': m, 'cobertura': cob}
    nome, prescricao, eixo_d, eixo_c = classificar(m['media'], cob['pct'])
    return {
        'zona': nome,
        'prescricao': prescricao,
        'eixo_desempenho': eixo_d,
        'eixo_cobertura': eixo_c,
        # ortogonal a zona: sensibilidade ao perfil de prova nao se corrige com
        # mais bloco tematico, so com prova inteira e diversa
        'variancia_alta': m['variancia_alta'],
        'acao_variancia': (
            'Desvio de %.1f pp entre blocos: inserir SIMULADO (prova inteira). '
            'Mais bloco por tema nao corrige sensibilidade a perfil de prova.'
            % m['desvio']) if m['variancia_alta'] else None,
        'metricas': m,
        'cobertura': cob,
    }


def simulado_check(db_path=None, janela=JANELA_SIMULADO_DIAS):
    """Ha simulado registrado na janela? Politica s126: 1/semana."""
    conn = _conn(db_path)
    row = conn.execute(
        "SELECT COUNT(*), MAX(data_sessao) FROM sessoes_bulk "
        "WHERE area = 'Simulado' AND data_sessao >= date('now', ?)",
        ('-%d day' % int(janela),)).fetchone()
    ultimo = conn.execute(
        "SELECT MAX(data_sessao) FROM sessoes_bulk WHERE area = 'Simulado'").fetchone()[0]
    conn.close()
    n = row[0] or 0
    return {'na_janela': n, 'janela_dias': janela, 'ultimo': ultimo,
            'em_debito': n == 0}


def _render(z, sim):
    m = z['metricas']
    if m.get('insuficiente'):
        return 'Blocos insuficientes para diagnostico (n=%d).' % m['n']
    out = ['# Diagnostico -- variancia e zona', '']
    out.append('- **Serie:** %d blocos (>= %dq) · media %.1f%% · **desvio %.1f pp** · '
               'amplitude %.1f pp (%.1f a %.1f)'
               % (m['n'], PISO_QUESTOES, m['media'], m['desvio'], m['amplitude'],
                  m['minimo'], m['maximo']))
    cob = z.get('cobertura') or {}
    if z.get('zona'):
        detalhe = (' · faltam %dq de %dq' % (cob['restante_q'], cob['total_grade_q'])
                   if cob.get('restante_q') else '')
        out.append('- **Zona: %s** (desempenho %s · cobertura %s = %.1f%% da grade%s)'
                   % (z['zona'], z['eixo_desempenho'], z['eixo_cobertura'],
                      cob['pct'], detalhe))
        out.append('  -> %s' % z['prescricao'])
    else:
        # sem grade/posicao nao da para cruzar os dois eixos -- dizer isso, nao inventar
        out.append('- **Zona: indefinida** (%s) -- a variancia abaixo segue valida.'
                   % z.get('motivo', 'sinal ausente'))
    if z.get('acao_variancia'):
        out.append('- 🔴 **Variancia alta:** %s' % z['acao_variancia'])
    else:
        out.append('- 🟢 Variancia dentro do esperado (< %.0f pp).' % DESVIO_ALERTA_PP)
    if sim['em_debito']:
        out.append('- ⚠️ **Simulado em debito:** nenhum nos ultimos %dd (ultimo: %s). '
                   'Politica: 1/semana.' % (sim['janela_dias'], sim['ultimo'] or 'nunca'))
    else:
        out.append('- 🟢 Simulado em dia (%d na janela de %dd).'
                   % (sim['na_janela'], sim['janela_dias']))
    ult = m['serie'][-8:]
    out.append('- Ultimos blocos: %s' % ', '.join('%.0f%%' % b['pct'] for b in ult))
    return '\n'.join(out)


def main(argv=None):
    p = argparse.ArgumentParser(description='Diagnostico de variancia e zona (MedHub)')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--metricas', action='store_true')
    g.add_argument('--zona', action='store_true')
    g.add_argument('--simulado-check', action='store_true')
    g.add_argument('--json', action='store_true', help='diagnostico completo em JSON')
    p.add_argument('--ultimos', type=int, help='usar so os N blocos mais recentes')
    p.add_argument('--piso', type=int, default=PISO_QUESTOES)
    args = p.parse_args(argv)

    if args.metricas:
        m = metricas(piso=args.piso, ultimos=args.ultimos)
        m.pop('serie', None)
        print(json.dumps(m, ensure_ascii=False, indent=2))
        return 0
    if args.simulado_check:
        print(json.dumps(simulado_check(), ensure_ascii=False, indent=2))
        return 0
    z = zona(piso=args.piso, ultimos=args.ultimos)
    sim = simulado_check()
    if args.json:
        z['simulado'] = sim
        z['metricas'].pop('serie', None)
        print(json.dumps(z, ensure_ascii=False, indent=2))
        return 0
    print(_render(z, sim))
    return 0


if __name__ == '__main__':
    sys.exit(main())
