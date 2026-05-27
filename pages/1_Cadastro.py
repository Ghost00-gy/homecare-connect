import streamlit as st
import sqlite3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.auth import hash_password

st.set_page_config(page_title="Cadastro - HomeCare Connect", page_icon="🩺")
st.markdown("<style>.stApp { background-color: #ffffff; }</style>", unsafe_allow_html=True)

st.title("Crie sua conta")

tipo_usuario = st.radio("Você é:", ["Paciente / Familiar", "Especialista da Saúde"])

with st.form("form_cadastro"):
    st.subheader("Dados de Acesso")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    nome = st.text_input("Nome Completo")
    
    if tipo_usuario == "Paciente / Familiar":
        st.markdown("#### Triagem do Paciente")
        localizacao = st.text_input("Localização (Endereço / Bairro / Cidade)", help="Precisamos da localização para a triagem e busca de profissionais próximos.")
        tipo_cuidado = st.text_area("Descreva brevemente o tipo de cuidado necessário")
        
    else:
        st.markdown("#### Cadastro de Especialista")
        especialidade = st.selectbox("Especialidade", ["Técnico de Enfermagem", "Enfermeiro", "Fisioterapeuta", "Médico", "Cuidador", "Nutricionista"])
        registro = st.text_input("Validação do Registro Profissional (COREN, CRM, CREFITO, etc.)", help="Obrigatório para atuar na plataforma.")
        regiao = st.text_input("Regiões que atende")
        valor = st.number_input("Valor médio do atendimento (R$)", min_value=0.0, format="%.2f")
        
    aceite_termos = st.checkbox("Li e aceito os termos de privacidade e uso de dados (Adequação LGPD)")
    submit = st.form_submit_button("Finalizar Cadastro")
    
    if submit:
        if not aceite_termos:
            st.error("Você precisa aceitar os termos de privacidade.")
        elif not email or not senha or not nome:
            st.warning("Preencha todos os dados de acesso básicos.")
        elif tipo_usuario == "Paciente / Familiar" and not localizacao:
            st.warning("A localização é obrigatória para a triagem de pacientes.")
        elif tipo_usuario == "Especialista da Saúde" and not registro:
            st.warning("A validação do registro profissional é obrigatória para os especialistas.")
        else:
            try:
                db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'homecare.db')
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                
                senha_hash = hash_password(senha)
                role = 'paciente' if tipo_usuario == "Paciente / Familiar" else 'profissional'
                
                c.execute("INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)", (email, senha_hash, role))
                user_id = c.lastrowid
                
                if role == 'paciente':
                    c.execute("INSERT INTO patients (user_id, nome_completo, localizacao, tipo_cuidado_necessario) VALUES (?, ?, ?, ?)", 
                              (user_id, nome, localizacao, tipo_cuidado))
                else:
                    c.execute("INSERT INTO professionals (user_id, nome_completo, especialidade, registro_profissional, regiao_atendimento, valor_consulta) VALUES (?, ?, ?, ?, ?, ?)", 
                              (user_id, nome, especialidade, registro, regiao, valor))
                
                conn.commit()
                st.success("Cadastro realizado com sucesso! Volte para a página inicial (Aplicativo) para fazer o login.")
            except sqlite3.IntegrityError:
                st.error("Este e-mail já está cadastrado em nosso sistema.")
            finally:
                conn.close()