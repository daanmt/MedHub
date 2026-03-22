import streamlit as st
import sqlite3
import pandas as pd
import random
import os

st.set_page_config(page_title="Central de Erros", page_icon="📓", layout="wide")
DB_PATH = 'ipub.db'

tab1, tab2 = st.tabs(["📖 Caderno de Erros (Consulta)", "🧠 FSRS Player (Reter)"])

# ── LOGICA CADERNO DE ERROS ──────────────────────────────────────────────────
with tab1:
    st.markdown('<p style="color: #A8B3C2;">Sua fonte primária dos elos quebrados, lida diretamente do SQLite `questoes_erros`.</p>', unsafe_allow_html=True)
    
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        try:
            df_erros = pd.read_sql_query("""
                SELECT q.id, t.area, t.tema, q.titulo, q.elo_quebrado, q.caso, q.explicacao_correta, q.armadilha_prova
                FROM questoes_erros q
                JOIN taxonomia_cronograma t ON q.tema_id = t.id
                ORDER BY q.id DESC
            """, conn)
        except Exception:
            # Fallback seguro para esquemas cacheados (sem a coluna armadilha_prova)
            df_erros = pd.read_sql_query("""
                SELECT q.id, t.area, t.tema, q.titulo, q.elo_quebrado, q.caso, q.explicacao_correta, 'N/A' as armadilha_prova
                FROM questoes_erros q
                JOIN taxonomia_cronograma t ON q.tema_id = t.id
                ORDER BY q.id DESC
            """, conn)
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
        SELECT f.id, f.frente, f.verso, t.area, t.tema, c.state
        FROM flashcards f
        JOIN taxonomia_cronograma t ON f.tema_id = t.id
        JOIN fsrs_cards c ON f.id = c.card_id
        WHERE c.due <= datetime('now') OR c.state = 0
        ''')
        rows = c.fetchall()
        return [{"id": r[0], "frente": r[1], "verso": r[2], "area": r[3], "tema": r[4], "state": r[5]} for r in rows]

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
                    try:
                        con = sqlite3.connect(DB_PATH)
                        dias = {1:0, 2:1, 3:3, 4:7}[rating]
                        con.execute(f"UPDATE fsrs_cards SET state=2, due=datetime('now', '+{dias} days') WHERE card_id=?", (card['id'],))
                        con.commit()
                        con.close()
                    except: pass
                st.session_state.fc_idx += 1
                st.session_state.fc_verso = False
                if st.session_state.fc_idx >= total:
                    st.cache_data.clear()
                    st.session_state.pop('fc_order', None)
                st.rerun()

            st.markdown(f"**📚 {card['area']} › {card['tema']}**")
            
            if not st.session_state.fc_verso:
                st.markdown(f'<div style="background:#11161D; border:1px solid #202A36; padding:20px; border-radius:12px; font-size:1.1rem;">{card["frente"]}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Revelar", type='primary', width='stretch'):
                    st.session_state.fc_verso = True
                    st.rerun()
                if st.button("⏭️ Pular"): _avancar(0)
            else:
                st.markdown(f'<div style="background:#1A1F26; border:1px solid #2F6BFF; border-left:4px solid #2F6BFF; padding:20px; border-radius:12px; font-size:1.1rem;">{card["verso"]}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                b1, b2, b3, b4 = st.columns(4)
                if b1.button("Novamente", width='stretch'): _avancar(1)
                if b2.button("Difícil (1d)", width='stretch'): _avancar(2)
                if b3.button("Bom (3d)", width='stretch'): _avancar(3)
                if b4.button("Fácil (7d)", width='stretch'): _avancar(4)
