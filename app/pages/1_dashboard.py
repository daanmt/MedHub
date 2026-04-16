import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

from app.utils.styles import inject_styles, content_card, COLORS
from app.engine import summarize_performance

st.set_page_config(page_title="MedHub Dashboard", page_icon="📊", layout="wide")
inject_styles()
DB_PATH = 'ipub.db'

# ──────────────────────────────────────────────────────────
# DATA LAYER
# ──────────────────────────────────────────────────────────

def get_bulk_totals():
    """Agrega questoes_feitas / questoes_acertadas por área, da sessoes_bulk."""
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
    """Devolve série temporal por área para cálculo de tendência."""
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
            WHERE sessao_num > 0          -- exclui migração histórica
              AND questoes_feitas > 0
            ORDER BY area, sessao_num
        """, conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def get_erros_por_area():
    """Conta erros registrados no banco por área."""
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

def get_foco_critico():
    """Temas com baixo desempenho ou não revistos há muito tempo."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM taxonomia_cronograma", conn)
        df['dias_sem_ver'] = (
            datetime.now() - pd.to_datetime(df['ultima_revisao'])
        ).dt.days.fillna(999)
        df = df[(df['questoes_realizadas'] > 0) & (df['dias_sem_ver'] > 3)].copy()
        if not df.empty:
            df['fator_risco'] = df['dias_sem_ver'] + ((100 - df['percentual_acertos']) * 0.5)
            df = df.sort_values('fator_risco', ascending=False)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

# ──────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────

def trend_badge(area, trend_df):
    """Retorna (emoji, cor, label) de tendência para uma área."""
    sub = trend_df[trend_df['area'] == area].sort_values('sessao_num')
    if len(sub) < 2:
        return "—", COLORS['muted_fg'], "Dados insuficientes"
    # Regressão simples: compara última vs média anterior
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
    if pct >= 75:
        return COLORS['success']
    elif pct >= 60:
        return COLORS['warning']
    return COLORS['danger']

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

    # ── Métricas topo ──
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Questões (EMED)", f"{total_q:,}".replace(",", "."))
    m2.metric("Acertos",         f"{total_a:,}".replace(",", "."))
    m3.metric("Desempenho Geral", f"{perf_geral:.1f}%")
    m4.metric("Erros estruturados", total_err)

    st.divider()

    # ── Linha 1: Gráfico + Foco Crítico ──
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
        fig.add_vline(x=70, line_dash="dot", line_color=COLORS['warning'],
                      annotation_text="Meta 70%", annotation_position="top right",
                      annotation_font_color=COLORS['warning'])
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
        st.caption("Temas com baixa performance ou não vistos há muito tempo.")
        df_fc = get_foco_critico()
        if not df_fc.empty:
            for _, r in df_fc.head(8).iterrows():
                pct_color = color_for_pct(r['percentual_acertos'])
                st.markdown(f"""
                <div style="background:#11161D;border-left:3px solid {COLORS['danger']};
                            border-radius:6px;padding:10px;margin-bottom:8px;">
                    <div style="font-size:0.8rem;color:{COLORS['secondary_fg']};">{r['area']}</div>
                    <div style="font-weight:600;color:{COLORS['foreground']};">{r['tema']}</div>
                    <div style="font-size:0.8rem;color:{pct_color};">
                        {r['percentual_acertos']:.1f}% acertos
                        &nbsp;·&nbsp; há {int(r['dias_sem_ver'])} dias
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 Nenhum tema crítico para revisão urgente hoje.")

    st.divider()

    # ── Linha 2: Tabela de desempenho + Tendência ──
    col_t, col_trend = st.columns([1.5, 1])

    with col_t:
        st.subheader("📋 Resumo por Especialidade")
        df_display = df_bulk.copy()
        df_display['Erros reg.'] = df_display['area'].map(
            df_erros.set_index('area')['erros'] if not df_erros.empty else {}
        ).fillna(0).astype(int)
        df_display['% Acerto'] = df_display['pct'].apply(lambda x: f"{x:.1f}%")
        df_display.rename(columns={
            'area': 'Especialidade',
            'feitas': 'Feitas',
            'acertos': 'Acertos',
            'sessoes': 'Sessões',
        }, inplace=True)
        st.dataframe(
            df_display[['Especialidade','Feitas','Acertos','% Acerto','Erros reg.','Sessões']],
            use_container_width=True,
            hide_index=True,
        )

    with col_trend:
        st.subheader("📉 Tendência por Área")
        has_trend = not df_trend.empty
        if has_trend:
            areas_com_trend = df_trend['area'].unique()
            for area in areas_com_trend:
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
            st.info("Tendência disponível a partir da 2ª sessão por área.\n\n"
                    "Use `registrar_sessao_bulk.py` após cada sessão para ativar.")

    # ── Linha 3: Gráfico de evolução temporal (se houver ≥2 sessões) ──
    if has_trend and len(df_trend['sessao_num'].unique()) >= 2:
        st.divider()
        st.subheader("📅 Evolução Temporal da Performance")
        fig2 = px.line(
            df_trend, x='sessao_num', y='pct', color='area',
            markers=True,
            labels={'sessao_num': 'Sessão', 'pct': 'Aproveitamento (%)', 'area': 'Área'},
            template='plotly_dark',
        )
        fig2.add_hline(y=70, line_dash="dot", line_color=COLORS['warning'])
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
    st.info("Banco de dados vazio ou sem dados de sessão. "
            "Execute `tools/migrar_sessoes_bulk.py` para inicializar.")

# ── Padrões de Fraqueza (memória cross-session) ──
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
