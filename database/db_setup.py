import sqlite3
import os

def init_db():
    db_path = os.path.join(os.path.dirname(__file__), 'homecare.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Tabela Base de Usuários
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Tabela de Pacientes (Localização exigida na triagem)
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            user_id INTEGER PRIMARY KEY,
            nome_completo TEXT,
            localizacao TEXT NOT NULL,
            tipo_cuidado_necessario TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Tabela de Profissionais (Validação exigida no cadastro de especialista)
    c.execute('''
        CREATE TABLE IF NOT EXISTS professionals (
            user_id INTEGER PRIMARY KEY,
            nome_completo TEXT,
            especialidade TEXT,
            registro_profissional TEXT NOT NULL,
            regiao_atendimento TEXT,
            valor_consulta REAL,
            status_aprovacao TEXT DEFAULT 'pendente',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    init_db()