import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Meus Atendimentos", page_icon="📋", layout="wide")

# Força o fundo branco para manter a identidade visual limpa
st.markdown("<style>.stApp { background-color: #ffffff; }</style>", unsafe_allow_html=True)

st.title("📋 Meus Atendimentos")

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Você precisa fazer login para acessar seus atendimentos.")
else:
    # Conecta ao banco de dados
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'homecare.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Cria a tabela de atendimentos caso ainda não exista no SQLite
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            professional_id INTEGER,
            status TEXT DEFAULT 'Pendente',
            data_solicitacao TEXT,
            FOREIGN KEY(patient_id) REFERENCES users(id),
            FOREIGN KEY(professional_id) REFERENCES users(id)
        )
    ''')
    conn.commit()

    user_id = st.session_state['user_id']
    user_role = st.session_state['user_role']

    st.markdown("---")

    if user_role == 'paciente':
        st.subheader("Solicitações Enviadas")
        
        # Busca os pedidos feitos por este paciente
        query = '''
            SELECT a.id, p.nome_completo AS profissional, p.especialidade, a.status, a.data_solicitacao
            FROM appointments a
            JOIN professionals p ON a.professional_id = p.user_id
            WHERE a.patient_id = ?
        '''
        df_pedidos = pd.read_sql_query(query, conn, params=(user_id,))
        
        if df_pedidos.empty:
            st.info("Você ainda não solicitou nenhum atendimento.")
        else:
            st.dataframe(df_pedidos, use_container_width=True, hide_index=True)

    elif user_role == 'profissional':
        st.subheader("Solicitações Recebidas")
        
        # Busca os pedidos recebidos por este profissional
        query = '''
            SELECT a.id, pt.nome_completo AS paciente, pt.localizacao, pt.tipo_cuidado_necessario, a.status, a.data_solicitacao
            FROM appointments a
            JOIN patients pt ON a.patient_id = pt.user_id
            WHERE a.professional_id = ?
        '''
        df_recebidos = pd.read_sql_query(query, conn, params=(user_id,))
        
        if df_recebidos.empty:
            st.info("Você não possui novas solicitações no momento.")
        else:
            for index, row in df_recebidos.iterrows():
                with st.container():
                    st.markdown(f"**Paciente:** {row['paciente']}")
                    st.markdown(f"**Localização:** {row['localizacao']}")
                    st.markdown(f"**Necessidade:** {row['tipo_cuidado_necessario']}")
                    st.markdown(f"**Status Atual:** `{row['status']}`")
                    
                    if row['status'] == 'Pendente':
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Aceitar", key=f"aceitar_{row['id']}"):
                                c.execute("UPDATE appointments SET status = 'Aceito' WHERE id = ?", (row['id'],))
                                conn.commit()
                                st.rerun()
                        with col2:
                            if st.button("❌ Recusar", key=f"recusar_{row['id']}"):
                                c.execute("UPDATE appointments SET status = 'Recusado' WHERE id = ?", (row['id'],))
                                conn.commit()
                                st.rerun()
                    st.markdown("---")
    
    conn.close()