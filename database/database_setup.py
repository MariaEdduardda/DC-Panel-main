import sqlite3

def create_database():
    conn = sqlite3.connect("gfo_system.db")
    cursor = conn.cursor()

    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT CHECK(perfil IN ('operador', 'coordenador', 'gestor')) NOT NULL
        );
    """)

    # Tabela de Ocorrências
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ocorrencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT CHECK(tipo IN ('audio', 'video', 'automacao', 'transmissao', 'logo')) NOT NULL,
            descricao TEXT NOT NULL,
            gravidade TEXT CHECK(gravidade IN ('leve', 'media', 'grave', 'gravissima')) NOT NULL,
            origem TEXT CHECK(origem IN ('Rede', 'RSPO', 'G5')) NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            duracao TEXT,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        );
    """)

    # Tabela de Classificação (revisões)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ocorrencia_id INTEGER NOT NULL,
            revisado_por INTEGER NOT NULL,
            gravidade_atualizada TEXT CHECK(gravidade_atualizada IN ('leve', 'media', 'grave', 'gravissima')),
            origem_atualizada TEXT CHECK(origem_atualizada IN ('Rede', 'RSPO', 'G5')),
            data TEXT NOT NULL,
            FOREIGN KEY (ocorrencia_id) REFERENCES ocorrencias (id),
            FOREIGN KEY (revisado_por) REFERENCES usuarios (id)
        );
    """)

    # Tabela de Relatórios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relatorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            periodo TEXT NOT NULL,
            total_falhas INTEGER DEFAULT 0,
            total_gravissimas INTEGER DEFAULT 0,
            total_leves INTEGER DEFAULT 0,
            gerado_por INTEGER NOT NULL,
            FOREIGN KEY (gerado_por) REFERENCES usuarios (id)
        );
    """)

    conn.commit()
    conn.close()
    print(" Banco de dados 'gfo_system.db' criado com sucesso!")


if __name__ == "__main__":
    create_database()
