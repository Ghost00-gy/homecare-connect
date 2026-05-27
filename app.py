import streamlit as st
import sqlite3
import os
from utils.auth import check_password

st.set_page_config(page_title="HomeCare Connect", page_icon="🩺", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.image("assets/logo.png", width=250)

st.title("🩺 HomeCare Connect")
st.markdown("### Cuidado humanizado e profissional no conforto do seu lar.")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state['user_id'] = None

if not st.session_state['logged_in']:
    st.subheader("Acesso ao Sistema")
    
    with st.form("form_login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        submit_login = st.form_submit_button("Entrar")
        
        if submit_login:
            db_path = os.path.join(os.path.dirname(__file__), 'database', 'homecare.db')
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            c.execute("SELECT id, password_hash, role FROM users WHERE email = ?", (email,))
            user = c.fetchone()
            conn.close()
            
            if user and check_password(senha, user[1]):
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user[0]
                st.session_state['user_role'] = user[2]
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")
                
    st.info("Ainda não tem conta? Acesse a página de **1 Cadastro** no menu lateral.")

else:
    st.success("Você está logado no sistema!")
    st.write(f"**Nível de acesso:** {st.session_state['user_role'].capitalize()}")
    
    st.markdown("---")
    st.markdown("Utilize o menu lateral para navegar entre as funcionalidades.")
    
    if st.button("Sair da Conta"):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.session_state['user_id'] = None
        st.rerun()