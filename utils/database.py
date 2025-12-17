import sqlite3
import os
import hashlib
import csv
import io
from datetime import datetime

DATABASE_DIR = "data"
DATABASE = os.path.join(DATABASE_DIR, "estoque.db")
ASSETS_DIR = "assets"

# Garante diretórios
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    conn = get_db_connection()
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
            data_validade TEXT,
            vendido INTEGER DEFAULT 0,
            data_ultima_venda TEXT
        );
    """)
    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
    """)
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                        ("admin", hash_password("123"), "admin"))
    except sqlite3.IntegrityError:
        pass 
    conn.commit()
    conn.close()

create_tables()

# --- CRUD CORRIGIDO ---

def get_all_produtos(include_sold=True):
    """Busca produtos. Se include_sold=True, traz inclusive os com quantidade 0."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if include_sold:
        cursor.execute("SELECT * FROM produtos ORDER BY nome ASC")
    else:
        cursor.execute("SELECT * FROM produtos WHERE quantidade > 0 ORDER BY nome ASC")
    
    produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return produtos

def update_produto(product_id, nome, preco, quantidade, marca, estilo, tipo, foto, data_validade):
    """Atualiza sem risco de deletar o produto."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produtos 
        SET nome=?, preco=?, quantidade=?, marca=?, estilo=?, tipo=?, foto=?, data_validade=?
        WHERE id=?
    """, (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade, product_id))
    conn.commit()
    conn.close()

def mark_produto_as_sold(product_id, quantity_sold=1):
    """Diminui o estoque sem remover o produto da tabela."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Verifica se existe estoque
    cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (product_id,))
    res = cursor.fetchone()
    if res and res['quantidade'] >= quantity_sold:
        cursor.execute("""
            UPDATE produtos 
            SET quantidade = quantidade - ?, 
                vendido = 1, 
                data_ultima_venda = ? 
            WHERE id = ?
        """, (quantity_sold, datetime.now().isoformat(), product_id))
        conn.commit()
    conn.close()

def get_produto_by_id(p_id):
    conn = get_db_connection()
    res = conn.execute("SELECT * FROM produtos WHERE id = ?", (p_id,)).fetchone()
    conn.close()
    return dict(res) if res else None
