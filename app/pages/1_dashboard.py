import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os

from app.utils.styles import inject_styles, content_card, COLORS
from app.engine import summarize_performance

st.set_page_config(page_title="MedHub Dashboard", page_icon="📊", layout="wide")
inject_styles()
DB_PATH = 'ipub.db'
META_PCT = 85  # ← meta de aproveitamento

# ──────────────────────────────────────────────────────────
# DATA LAYER
# ──────────────────────────────────────────────────────────

def get_bulk_totals():
    """Agrega questoes_feitas / acertadas por área, da sessoes_bulk."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("""
            SELECT
                area,
                SUM(questoes_feitas)     AS feitas,
                SUM(questoes_acertadas)  AS acertos,
                COUNT(DISTINCT sessao_num) AS sessoes,
                MAX(data_sessao)           AS ultima_sessao
            FROM sessoes_bulk
            WHERE questoes_feitas > 0
            GROUP BY area
            ORDER BY feitas DESC
        """, conn)
        df['pct'] = (df['acertos'] / df['feitas'] * 100).round(1)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def get_trend_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("""
            SELECT sessao_num, area, questoes_feitas, questoes_acertadas,
                   data_sessao,
                   CASE WHEN questoes_feitas > 0
                        THEN CAST(questoes_acertadas AS REAL) / questoes_feitas * 100
                        ELSE 0 END AS pct
            FROM sessoes_bulk
            WHERE sessao_num > 0
              AND questoes_feitas > 0
            ORDER BY area, sessao_num
        """, conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def get_erros_por_area():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("""
            SELECT t.area, COUNT(q.id) AS erros
            FROM questoes_erros q
            JOIN taxonomia_cronograma t ON t.id = q.tema_id
            GROUP BY t.area
        """, conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def get_foco_critico(df_bulk: pd.DataFrame):
    """
    Calcula Foco Crítico a partir de sessoes_bulk (timestamps reais).
    Critérios:
      - Não vista há > 7 dias: urgente
      - % acerto < meta: precisa reforço  
      - Fator de risco = dias_sem_ver * (1 + penalidade_pct)
    """
    if df_bulk.empty:
        return pd.DataFrame()
    today = date.today()
    rows = []
    for _, r in df_bulk.iterrows():
        ultima = r.get('ultima_sessao')
        if ultima:
            try:
                dt = datetime.strptime(str(ultima)[:10], '%Y-%m-%d').date()
                dias = (today - dt).days
            except Exception:
                dias = 999
        else:
            dias = 999

        pct = r['pct']
        penalidade = max(0, META_PCT - pct) / 10  # cada 1% abaixo da meta = 0.1 ponto
        fator = dias * (1 + penalidade)

        rows.append({
            'area':       r['area'],
            'feitas':     int(r['feitas']),
            'acertos':    int(r['acertos']),
            'pct':        pct,
            'ultima_sessao': ultima or '—',
            'dias_sem_ver':  dias,
            'fator_risco':   fator,
        })
    df = pd.DataFrame(rows)
    return df.sort_values('fator_risco', ascending=False)

# ──────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────

def trend_badge(area, trend_df):
    sub = trend_df[trend_df['area'] == area].sort_values('sessao_num')
    if len(sub) < 2:
        return "—", COLORS['muted_fg'], "Aguardando 2ª sessão"
    last   = sub['pct'].iloc[-1]
    before = sub['pct'].iloc[:-1].mean()
    delta  = last - before
    if delta >= 3:
        return "↑", COLORS['success'], f"+{delta:.1f}% vs média anterior"
    elif delta <= -3:
        return "↓", COLORS['danger'],  f"{delta:.1f}% vs média anterior"
    else:
        return "→", COLORS['warning'], f"{delta:+.1f}% — estável"

def color_for_pct(pct):
    if pct >= META_PCT:
        return COLORS['success']
    elif pct >= 60:
        return COLORS['warning']
    return COLORS['danger']

def urgency_color(dias):
    if dias > 30:  return COLORS['danger']
    if dias > 14:  return COLORS['warning']
    return COLORS['secondary_fg']

def dias_label(dias):
    if dias == 999:  return "nunca registrada"
    if dias == 0:    return "hoje"
    if dias == 1:    return "há 1 dia"
    return f"há {dias} dias"

# ──────────────────────────────────────────────────────────
# LAYOUT
# ──────────────────────────────────────────────────────────

st.title("📊 Painel Central")
st.markdown(
    '<p style="color:#A8B3C2;margin-top:-15px;margin-bottom:30px;">A Métrica como Bússola.</p>',
    unsafe_allow_html=True
)

df_bulk  = get_bulk_totals()
df_trend = get_trend_data()
df_erros = get_erros_por_area()

has_data = df_bulk is not None and not df_bulk.empty

if has_data:
    total_q   = int(df_bulk['feitas'].sum())
    total_a   = int(df_bulk['acertos'].sum())
    total_err = int(df_erros['erros'].sum()) if not df_erros.empty else 0
    perf_geral = (total_a / total_q * 100) if total_q else 0
    acima_meta = int((df_bulk['pct'] >= META_PCT).sum())

    # ── Métricas topo ──
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Questões (EMED)", f"{total_q:,}".replace(",", "."))
    m2.metric("Acertos",         f"{total_a:,}".replace(",", "."))
    m3.metric("Desempenho Geral", f"{perf_geral:.1f}%",
              delta=f"{perf_geral - META_PCT:.1f}% vs meta {META_PCT}%",
              delta_color="normal")
    m4.metric("Erros estruturados", total_err)
    m5.metric(f"Acima da meta {META_PCT}%", f"{acima_meta}/{len(df_bulk)} áreas")

    st.divider()

    # ── Linha 1: Gráfico bar + Foco Crítico ──
    c1, c2 = st.columns([1.6, 1])

    with c1:
        st.subheader("📈 Aproveitamento por Especialidade")
        df_chart = df_bulk.sort_values('pct')
        bar_colors = [color_for_pct(p) for p in df_chart['pct']]

        fig = go.Figure(go.Bar(
            x=df_chart['pct'],
            y=df_chart['area'],
            orientation='h',
            marker_color=bar_colors,
            text=[f"{p:.1f}%" for p in df_chart['pct']],
            textposition='inside',
            textfont=dict(color='white', size=11),
            hovertemplate='<b>%{y}</b><br>%{x:.1f}% — '
                          '%{customdata[0]} / %{customdata[1]} questões<extra></extra>',
            customdata=df_chart[['acertos', 'feitas']].values,
        ))
        fig.add_vline(
            x=META_PCT,
            line_dash="dot",
            line_color=COLORS['warning'],
            annotation_text=f"Meta {META_PCT}%",
            annotation_position="top right",
            annotation_font_color=COLORS['warning'],
        )
        fig.update_layout(
            xaxis_range=[0, 100],
            xaxis_title="Aproveitamento (%)",
            yaxis_title=None,
            margin=dict(l=0, r=20, t=10, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['foreground']),
            height=420,
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🚨 Foco Crítico")
        st.caption(f"Ordenado por: tempo sem ver + distância da meta {META_PCT}%.")

        df_fc = get_foco_critico(df_bulk)
        if not df_fc.empty:
            # Exibe top 8
            for _, r in df_fc.head(8).iterrows():
                pct_color = color_for_pct(r['pct'])
                dias_c    = urgency_color(r['dias_sem_ver'])
                abaixo    = r['pct'] < META_PCT
                border    = COLORS['danger'] if abaixo else COLORS['border']

                # Badge de ação recomendada
                if r['dias_sem_ver'] > 14:
                    acao = "⏰ Rever"
                elif abaixo:
                    acao = "📖 Reforço"
                else:
                    acao = "✅ OK"

                st.markdown(f"""
                <div style="background:#11161D;border-left:3px solid {border};
                            border-radius:6px;padding:10px;margin-bottom:8px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-size:0.8rem;color:{COLORS['secondary_fg']};">{r['area']}</div>
                    <div style="font-size:0.75rem;color:{dias_c};">{dias_label(r['dias_sem_ver'])}</div>
                  </div>
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px;">
                    <div style="font-size:0.8rem;color:{pct_color};font-weight:600;">{r['pct']:.1f}% acerto</div>
                    <div style="font-size:0.72rem;color:{COLORS['muted_fg']};">{acao}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Sem dados de sessão para calcular foco crítico.")

    st.divider()

    # ── Linha 2: Tabela de desempenho + Tendência ──
    col_t, col_trend = st.columns([1.5, 1])

    with col_t:
        st.subheader("📋 Resumo por Especialidade")
        df_display = df_bulk.copy()
        erros_map = df_erros.set_index('area')['erros'] if not df_erros.empty else {}
        df_display['Erros reg.'] = df_display['area'].map(erros_map).fillna(0).astype(int)
        df_display['% Acerto'] = df_display['pct'].apply(lambda x: f"{x:.1f}%")
        df_display['Última sessão'] = df_display['ultima_sessao'].apply(
            lambda x: str(x)[:10] if x else '—'
        )
        df_display.rename(columns={
            'area': 'Especialidade',
            'feitas': 'Feitas',
            'acertos': 'Acertos',
            'sessoes': 'Sessões',
        }, inplace=True)
        st.dataframe(
            df_display[['Especialidade','Feitas','Acertos','% Acerto','Erros reg.','Última sessão','Sessões']],
            use_container_width=True,
            hide_index=True,
        )

    with col_trend:
        st.subheader("📉 Tendência por Área")
        has_trend = not df_trend.empty
        if has_trend:
            for area in df_trend['area'].unique():
                arrow, color, label = trend_badge(area, df_trend)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;
                            margin-bottom:8px;padding:8px 12px;
                            background:#11161D;border-radius:8px;">
                    <span style="font-size:1.1rem;color:{color};font-weight:700;">{arrow}</span>
                    <div>
                        <div style="font-weight:600;font-size:0.9rem;">{area}</div>
                        <div style="font-size:0.75rem;color:{COLORS['muted_fg']};">{label}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(
                "📈 Tendência ativa após 2ª sessão por área.\n\n"
                "Use `tools/registrar_sessao_bulk.py` ao final de cada sessão."
            )

    # ── Linha 3: Evolução temporal ──
    if has_trend and len(df_trend['sessao_num'].unique()) >= 2:
        st.divider()
        st.subheader("📅 Evolução Temporal da Performance")
        fig2 = px.line(
            df_trend, x='sessao_num', y='pct', color='area',
            markers=True,
            labels={'sessao_num': 'Sessão', 'pct': 'Aproveitamento (%)', 'area': 'Área'},
            template='plotly_dark',
        )
        fig2.add_hline(y=META_PCT, line_dash="dot", line_color=COLORS['warning'],
                       annotation_text=f"Meta {META_PCT}%", annotation_font_color=COLORS['warning'])
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis_range=[0, 100],
            font=dict(color=COLORS['foreground']),
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Banco de dados vazio. Execute `tools/migrar_sessoes_bulk.py` para inicializar.")

# ── Padrões de Fraqueza ──
perf = summarize_performance()
if perf["padroes"]:
    st.divider()
    st.markdown("### 🧠 Padrões de Fraqueza (Memória Cross-Session)")
    for p in perf["padroes"]:
        content_card(
            title=p["area"],
            content=f"{p['pattern']} — {p['error_count']} erros",
            subtitle=p.get("especialidade") or None,
        )
