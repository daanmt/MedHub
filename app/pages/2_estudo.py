import streamlit as st
import sqlite3
import pandas as pd
import random
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.utils.db import record_review

st.set_page_config(page_title="Central de Erros", page_icon="📓", layout="wide")
import os as _os
DB_PATH = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))), 'ipub.db')

tab1, tab2 = st.tabs(["📖 Caderno de Erros (Consulta)", "🧠 FSRS Player (Reter)"])

# ── LOGICA CADERNO DE ERROS ──────────────────────────────────────────────────
with tab1:
    st.markdown('<p style="color: #A8B3C2;">Sua fonte primária dos elos quebrados, lida diretamente do SQLite `questoes_erros`.</p>', unsafe_allow_html=True)
    
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        try:
            df_erros = pd.read_sql_query("""
                SELECT q.id, t.area, t.tema, q.titulo,
                       q.habilidades_sequenciais AS elo_quebrado,
                       q.o_que_faltou AS caso,
                       q.explicacao_correta, q.armadilha_prova
                FROM questoes_erros q
                JOIN taxonomia_cronograma t ON q.tema_id = t.id
                ORDER BY q.id DESC
            """, conn)
        except Exception as e1:
            try:
                # Fallback ultra-seguro para esquemas estruturais desconhecidos do Cloud
                df_erros = pd.read_sql_query("""
                    SELECT q.*, t.area, t.tema 
                    FROM questoes_erros q
                    JOIN taxonomia_cronograma t ON q.tema_id = t.id
                    ORDER BY q.id DESC
                """, conn)
                # Garante que a UI não quebre se colunas antigas faltarem
                for col in ['titulo', 'elo_quebrado', 'caso', 'explicacao_correta', 'armadilha_prova']:
                    if col not in df_erros.columns:
                        df_erros[col] = 'N/A'
            except Exception as e2:
                st.error(f"⚠️ Erro Fatal no Banco de Dados da Nuvem.")
                st.code(f"Erro original: {e1}\nFallback também falhou: {e2}")
                df_erros = pd.DataFrame()
        conn.close()
        
        if not df_erros.empty:
            areas = sorted(df_erros['area'].unique())
            filtro_area = st.multiselect("Filtrar Especialidade", areas, placeholder="Todas", key="filt_cad")
            
            f_df = df_erros[df_erros['area'].isin(filtro_area)] if filtro_area else df_erros
            
            for _, r in f_df.iterrows():
                with st.expander(f"Erro #{r['id']} · {r['titulo']}"):
                    st.caption(f"{r['area']} › {r['tema']}")
                    if r['elo_quebrado'] and r['elo_quebrado'] != 'N/A':
                        st.markdown(f"**🔗 Elo Quebrado:** {r['elo_quebrado']}")
                    if r['caso'] and r['caso'] != 'N/A':
                        st.markdown(f"**📝 Caso:** {r['caso']}")
                    if r['explicacao_correta'] and r['explicacao_correta'] != 'N/A':
                        st.success(f"{r['explicacao_correta']}")
                    if r['armadilha_prova'] and r['armadilha_prova'] != 'N/A':
                        st.warning(f"**Armadilha:** {r['armadilha_prova']}")
        else:
            st.info("Nenhum erro cadastrado ainda no banco de dados.")
    else:
        st.error("Banco de dados não encontrado.")

# ── LOGICA FSRS PLAYER ───────────────────────────────────────────────────────
with tab2:
    st.markdown('<p style="color: #A8B3C2;">Cards higienizados. Memorização ativa da carga cognitiva.</p>', unsafe_allow_html=True)
    
    @st.cache_data(ttl=60)
    def load_flashcards():
        if not os.path.exists(DB_PATH): return []
        c = sqlite3.connect(DB_PATH).cursor()
        c.execute('''
        SELECT f.id, f.frente, f.verso, t.area, t.tema, c.state,
               f.frente_contexto, f.frente_pergunta, f.verso_resposta,
               f.verso_regra_mestre, f.verso_armadilha
        FROM flashcards f
        LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
        JOIN fsrs_cards c ON f.id = c.card_id
        WHERE c.due <= datetime('now') OR c.state = 0
        ''')
        rows = c.fetchall()
        return [{"id": r[0], "frente": r[1], "verso": r[2],
                 "area": r[3] or "Geral", "tema": r[4] or "",
                 "state": r[5],
                 "frente_contexto": r[6], "frente_pergunta": r[7],
                 "verso_resposta": r[8], "verso_regra_mestre": r[9],
                 "verso_armadilha": r[10]} for r in rows]

    cards = load_flashcards()
    
    if not cards:
        st.success("🎉 Você zerou a fila de retenção! Todos os cards em dia.")
    else:
        # Filtros
        colf1, colf2 = st.columns([3, 1])
        with colf1:
            areas_fc = sorted(set(c['area'] for c in cards))
            area_f_fc = st.multiselect("Especialidade", areas_fc, default=areas_fc, key="filt_fc")
        with colf2:
            limpar = st.button("🔄 Sincronizar Fila")
            emb = st.toggle("Modo Aleatório", True)
            if limpar:
                st.cache_data.clear()
                for k in ['fc_order', 'fc_idx', 'fc_verso']: st.session_state.pop(k, None)
                st.rerun()

        filtered_fc = [c for c in cards if c['area'] in area_f_fc]
        
        if not filtered_fc:
            st.info("Filtro vazio.")
        else:
            total = len(filtered_fc)
            if 'fc_order' not in st.session_state or len(st.session_state.fc_order) != total:
                order = list(range(total))
                if emb: random.shuffle(order)
                st.session_state.fc_order = order
                st.session_state.fc_idx = 0
                st.session_state.fc_verso = False

            idx = st.session_state.fc_idx % total
            card = filtered_fc[st.session_state.fc_order[idx]]
            
            st.progress((idx + 1) / total, f"Progresso: {idx + 1}/{total}")
            
            def _avancar(rating):
                if rating > 0:
                    if 'reviewed_ids' not in st.session_state:
                        st.session_state.reviewed_ids = set()
                    if card['id'] not in st.session_state.reviewed_ids:
                        record_review(card['id'], rating)
                        st.session_state.reviewed_ids.add(card['id'])
                st.session_state.fc_idx += 1
                st.session_state.fc_verso = False
                if st.session_state.fc_idx >= total:
                    st.cache_data.clear()
                    st.session_state.pop('fc_order', None)
                    st.session_state.pop('reviewed_ids', None)
                st.rerun()

            st.markdown(f"**📚 {card['area']} › {card['tema']}**")

            # Decide renderização: estruturada (novos campos) ou legada (frente/verso)
            use_structured = bool(
                card.get('frente_pergunta') and card['frente_pergunta'].strip() and
                card.get('verso_resposta') and card['verso_resposta'].strip()
            )

            if not st.session_state.fc_verso:
                if use_structured:
                    if card.get('frente_contexto') and card['frente_contexto'].strip():
                        st.caption(card['frente_contexto'])
                    st.markdown(f'<div style="background:#11161D; border:1px solid #202A36; padding:20px; border-radius:12px; font-size:1.1rem;">{card["frente_pergunta"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="background:#11161D; border:1px solid #202A36; padding:20px; border-radius:12px; font-size:1.1rem;">{card["frente"]}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Revelar", type='primary', width='stretch'):
                    st.session_state.fc_verso = True
                    st.rerun()
                if st.button("⏭️ Pular"): _avancar(0)
            else:
                if use_structured:
                    st.success(card['verso_resposta'])
                    if card.get('verso_regra_mestre') and card['verso_regra_mestre'].strip():
                        st.info(f"**Regra mestre:** {card['verso_regra_mestre']}")
                    if card.get('verso_armadilha') and card['verso_armadilha'].strip():
                        st.warning(f"**Armadilha:** {card['verso_armadilha']}")
                else:
                    st.markdown(f'<div style="background:#1A1F26; border:1px solid #2F6BFF; border-left:4px solid #2F6BFF; padding:20px; border-radius:12px; font-size:1.1rem;">{card["verso"]}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                b1, b2, b3, b4 = st.columns(4)
                if b1.button("Novamente", width='stretch'): _avancar(1)
                if b2.button("Difícil (1d)", width='stretch'): _avancar(2)
                if b3.button("Bom (3d)", width='stretch'): _avancar(3)
                if b4.button("Fácil (7d)", width='stretch'): _avancar(4)
