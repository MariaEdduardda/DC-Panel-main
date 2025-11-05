import sqlite3
from tkinter import messagebox
import hashlib

DB_NAME = "gfo_system.db"

# ==========================================================
#  Função auxiliar para criptografar senhas
# ==========================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================================
# 🔌 Função genérica de conexão
# ==========================================================
def connect():
    return sqlite3.connect(DB_NAME)

# ==========================================================
#  CRUD - Usuários
# ==========================================================
def criar_usuario(nome, email, senha, perfil):
    try:
        conn = connect()
        cursor = conn.cursor()
        senha_hash = hash_password(senha)
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, perfil)
            VALUES (?, ?, ?, ?)
        """, (nome, email, senha_hash, perfil))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Usuário '{nome}' cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Email já cadastrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {e}")
    finally:
        conn.close()

def autenticar_usuario(email, senha):
    try:
        conn = connect()
        cursor = conn.cursor()
        senha_hash = hash_password(senha)
        cursor.execute("""
            SELECT id, nome, perfil FROM usuarios
            WHERE email = ? AND senha = ?
        """, (email, senha_hash))
        user = cursor.fetchone()
        return user  # retorna (id, nome, perfil)
    finally:
        conn.close()

def listar_usuarios():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, perfil FROM usuarios")
    users = cursor.fetchall()
    conn.close()
    return users

def deletar_usuario(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Usuário deletado com sucesso!")

# ==========================================================
#  CRUD - Ocorrências
# ==========================================================
def criar_ocorrencia(tipo, descricao, gravidade, origem, data, hora, duracao, usuario_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ocorrencias (tipo, descricao, gravidade, origem, data, hora, duracao, usuario_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (tipo, descricao, gravidade, origem, data, hora, duracao, usuario_id))
    conn.commit()
    conn.close()

def listar_ocorrencias():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM ocorrencias o
        ORDER BY o.data DESC, o.hora DESC
    """)
    ocorrencias = cursor.fetchall()
    conn.close()
    return ocorrencias



def atualizar_ocorrencia(ocorrencia_id, tipo, descricao, gravidade, origem, data, hora, duracao):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ocorrencias
        SET tipo=?, descricao=?, gravidade=?, origem=?, data=?, hora=?, duracao=?
        WHERE id=?
    """, (tipo, descricao, gravidade, origem, data, hora, duracao, ocorrencia_id))
    conn.commit()
    conn.close()

def deletar_ocorrencia(ocorrencia_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ocorrencias WHERE id=?", (ocorrencia_id,))
    conn.commit()
    conn.close()

# ==========================================================
#  CRUD - Classificações (Revisões)
# ==========================================================
def criar_classificacao(ocorrencia_id, revisado_por, gravidade_atualizada, origem_atualizada, data):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO classificacoes (ocorrencia_id, revisado_por, gravidade_atualizada, origem_atualizada, data)
        VALUES (?, ?, ?, ?, ?)
    """, (ocorrencia_id, revisado_por, gravidade_atualizada, origem_atualizada, data))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Classificação registrada com sucesso!")

def listar_classificacoes():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, o.descricao, u.nome, c.gravidade_atualizada, c.origem_atualizada, c.data
        FROM classificacoes c
        JOIN ocorrencias o ON c.ocorrencia_id = o.id
        JOIN usuarios u ON c.revisado_por = u.id
        ORDER BY c.data DESC
    """)
    classificacoes = cursor.fetchall()
    conn.close()
    return classificacoes

# ==========================================================
# CRUD - Relatórios
# ==========================================================
def criar_relatorio(periodo, total_falhas, total_gravissimas, total_leves, gerado_por):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO relatorios (periodo, total_falhas, total_gravissimas, total_leves, gerado_por)
        VALUES (?, ?, ?, ?, ?)
    """, (periodo, total_falhas, total_gravissimas, total_leves, gerado_por))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Relatório gerado com sucesso!")

def listar_relatorios():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, r.periodo, r.total_falhas, r.total_gravissimas, r.total_leves, u.nome
        FROM relatorios r
        JOIN usuarios u ON r.gerado_por = u.id
        ORDER BY r.id DESC
    """)
    relatorios = cursor.fetchall()
    conn.close()
    return relatorios