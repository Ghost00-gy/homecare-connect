import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Buscar Profissionais - HomeCare", page_icon="🩺", layout="wide")

# Mantém a consistência do fundo branco
st.markdown("<style>.stApp { background-color: #ffffff; }</style>", unsafe_allow_html=True)

st.title("🔍 Encontre o Especialista Ideal")

# Verifica se o usuário está logado
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Você precisa fazer login para buscar profissionais e solicitar atendimentos.")
    st.info("Acesse a página inicial (Aplicativo) no menu lateral para entrar na sua conta.")
else:
    # Conecta ao banco de dados
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'homecare.db')
    conn = sqlite3.connect(db_path)
    
    # Busca os profissionais cadastrados
    query = """
        SELECT user_id, nome_completo, especialidade, regiao_atendimento, valor_consulta 
        FROM professionals
    """
    df_profissionais = pd.read_sql_query(query, conn)

    if df_profissionais.empty:
        st.info("Nenhum profissional cadastrado no momento. Volte mais tarde!")
    else:
        # Filtro Lateral
        st.sidebar.header("Filtros de Busca")
        especialidades_disponiveis = df_profissionais['especialidade'].unique().tolist()
        especialidade_selecionada = st.sidebar.selectbox(
            "Filtrar por Especialidade", 
            options=["Todas"] + especialidades_disponiveis
        )

        # Aplica o filtro
        if especialidade_selecionada != "Todas":
            df_filtrado = df_profissionais[df_profissionais['especialidade'] == especialidade_selecionada]
        else:
            df_filtrado = df_profissionais

        # Exibição em Cards
        st.markdown("---")
        
        if df_filtrado.empty:
            st.warning("Nenhum profissional encontrado para esta especialidade.")
        else:
            # Cria um grid de 3 colunas para exibir os profissionais
            cols = st.columns(3)
            
            for index, row in df_filtrado.iterrows():
                col = cols[index % 3]
                with col:
                    # Cria um "card" visual
                    with st.container():
                        st.markdown(f"### {row['nome_completo']}")
                        st.markdown(f"**Especialidade:** {row['especialidade']}")
                        st.markdown(f"**Atuação:** {row['regiao_atendimento']}")
                        st.markdown(f"**Valor:** R$ {row['valor_consulta']:.2f}")
                        
                        # Botão de solicitar atendimento real
                        if st.session_state.get('user_role') == 'paciente':
                            if st.button("Solicitar Atendimento", key=f"btn_{row['user_id']}"):
                                try:
                                    c = conn.cursor()
                                    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
                                    
                                    # Salva o pedido na tabela appointments
                                    c.execute('''
                                        INSERT INTO appointments (patient_id, professional_id, status, data_solicitacao)
                                        VALUES (?, ?, ?, ?)
                                    ''', (st.session_state['user_id'], row['user_id'], 'Pendente', data_atual))
                                    
                                    conn.commit()
                                    st.success(f"Solicitação enviada para {row['nome_completo']} com sucesso!")
                                except Exception as e:
                                    st.error("Erro ao processar a solicitação. Tente novamente.")
                        
                        st.markdown("---")
    
    conn.close()