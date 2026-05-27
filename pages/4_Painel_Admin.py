import streamlit as st
import sqlite3
import pandas as pd
import os

st.sidebar.image("assets/logo.png", use_container_width=True)

st.set_page_config(page_title="Painel Admin - HomeCare", page_icon="⚙️", layout="wide")

st.markdown("<style>.stApp { background-color: #ffffff; }</style>", unsafe_allow_html=True)

st.title("⚙️ Painel Administrativo")

# Trava de segurança: apenas administradores podem acessar
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Você precisa fazer login para acessar o painel.")
elif st.session_state.get('user_role') != 'admin':
    st.error("Acesso restrito. Sua conta não tem permissão de administrador.")
else:
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'homecare.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    st.markdown("### Visão Geral")
    col1, col2, col3 = st.columns(3)
    
    # Busca as métricas
    c.execute("SELECT COUNT(*) FROM patients")
    pacientes_qtd = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM professionals")
    profissionais_qtd = c.fetchone()[0]
    
    # Tenta contar os atendimentos (trata caso a tabela ainda não exista)
    try:
        c.execute("SELECT COUNT(*) FROM appointments")
        atendimentos_qtd = c.fetchone()[0]
    except sqlite3.OperationalError:
        atendimentos_qtd = 0
    
    col1.metric("Pacientes Cadastrados", pacientes_qtd)
    col2.metric("Especialistas Cadastrados", profissionais_qtd)
    col3.metric("Atendimentos Solicitados", atendimentos_qtd)
    
    st.markdown("---")
    st.markdown("### Aprovação de Profissionais")
    st.info("Verifique a validação do registro profissional (COREN, CRM, etc.) antes de aprovar.")
    
    query_pendentes = """
        SELECT user_id, nome_completo, especialidade, registro_profissional 
        FROM professionals 
        WHERE status_aprovacao = 'pendente'
    """
    df_pendentes = pd.read_sql_query(query_pendentes, conn)
    
    if df_pendentes.empty:
        st.success("Não há profissionais pendentes de aprovação no momento.")
    else:
        for index, row in df_pendentes.iterrows():
            with st.container():
                col_info, col_btn = st.columns([3, 1])
                with col_info:
                    st.markdown(f"**{row['nome_completo']}** | {row['especialidade']}")
                    st.markdown(f"**Validação/Registro:** `{row['registro_profissional']}`")
                with col_btn:
                    if st.button("✅ Aprovar Cadastro", key=f"aprovar_{row['user_id']}"):
                        c.execute("UPDATE professionals SET status_aprovacao = 'aprovado' WHERE user_id = ?", (row['user_id'],))
                        conn.commit()
                        st.rerun()
            st.markdown("---")
            
    conn.close()