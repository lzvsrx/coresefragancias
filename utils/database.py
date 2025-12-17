import sqlite3
import hashlib
import os
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# Configurações de Pastas
DB_NAME = "estoque.db"
ASSETS_DIR = "assets"
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# Constantes para Selectboxes
MARCAS = ["Eudora", "Boticário", "Natura", "Avon", "Outros"]
ESTILOS = ["Feminino", "Masculino", "Infantil", "Unissex"]
TIPOS = ["Perfume", "Hidratante", "Maquiagem", "Cabelo", "Acessórios"]

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    # Tabela de Produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            marca TEXT,
            estilo TEXT,
            tipo TEXT,
            foto TEXT,
            data_validade TEXT
        )
    """)
    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# --- FUNÇÕES DE USUÁRIO ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password, role="staff"):
    conn = get_connection()
    try:
        conn.cursor().execute("INSERT INTO usuarios VALUES (?, ?, ?)", 
                            (username, hash_password(password), role))
        conn.commit()
    except: pass
    finally: conn.close()

def get_user(username):
    conn = get_connection()
    user = conn.cursor().execute("SELECT * FROM usuarios WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users():
    conn = get_connection()
    users = conn.cursor().execute("SELECT username, role FROM usuarios").fetchall()
    conn.close()
    return [dict(u) for u in users]

# --- FUNÇÕES DE PRODUTO (CORREÇÃO DOS ERROS) ---

def get_all_produtos(include_out_of_stock=True, include_sold=True):
    """
    Função atualizada para aceitar os argumentos que as páginas estão enviando.
    """
    conn = get_connection()
    query = "SELECT * FROM produtos"
    
    # Se não quiser fora de estoque, filtra quantidade > 0
    if not include_out_of_stock:
        query += " WHERE quantidade > 0"
        
    cursor = conn.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_produto_by_id(p_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM produtos WHERE id = ?", (p_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_produto(nome, preco, quantidade, marca, estilo, tipo, foto, validade):
    conn = get_connection()
    conn.execute("""INSERT INTO produtos (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
                 (nome, preco, quantidade, marca, estilo, tipo, foto, validade))
    conn.commit()
    conn.close()

def update_produto(p_id, nome, preco, quantidade, marca, estilo, tipo, foto, validade):
    conn = get_connection()
    conn.execute("""UPDATE produtos SET nome=?, preco=?, quantidade=?, marca=?, estilo=?, tipo=?, foto=?, data_validade=?
                 WHERE id=?""", (nome, preco, quantidade, marca, estilo, tipo, foto, validade, p_id))
    conn.commit()
    conn.close()

def delete_produto(p_id):
    conn = get_connection()
    conn.execute("DELETE FROM produtos WHERE id = ?", (p_id,))
    conn.commit()
    conn.close()

def mark_produto_as_sold(p_id, qtd_vendida=1):
    conn = get_connection()
    p = conn.execute("SELECT quantidade FROM produtos WHERE id = ?", (p_id,)).fetchone()
    if p and p['quantidade'] >= qtd_vendida:
        nova_qtd = p['quantidade'] - qtd_vendida
        conn.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_qtd, p_id))
        conn.commit()
    else:
        conn.close()
        raise ValueError("Estoque insuficiente")
    conn.close()

# --- EXPORTAÇÃO ---
def export_produtos_to_csv_content():
    produtos = get_all_produtos()
    df = pd.DataFrame(produtos)
    return df.to_csv(index=False)

def generate_stock_pdf_bytes():
    produtos = get_all_produtos(include_out_of_stock=False)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório de Estoque Ativo", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    for p in produtos:
        pdf.cell(0, 10, f"{p['nome']} - {p['marca']} | Qtd: {p['quantidade']} | R$ {p['preco']}", ln=True)
    return pdf.output(dest='S')

def import_produtos_from_csv_buffer(uploaded_file):
    df = pd.read_csv(uploaded_file)
    for _, row in df.iterrows():
        add_produto(row['nome'], row['preco'], row['quantidade'], row.get('marca'), row.get('estilo'), row.get('tipo'), None, row.get('data_validade'))
    return len(df)
