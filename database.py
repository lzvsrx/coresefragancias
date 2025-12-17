import sqlite3
import os
import hashlib
import csv
import io
from datetime import datetime

DATABASE_DIR = "data"
DATABASE = os.path.join(DATABASE_DIR, "estoque.db")
ASSETS_DIR = "assets"

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

# --- FUNÇÕES DE BUSCA (A chave para não sumir) ---

def get_all_produtos(include_sold=True):
    """
    Se include_sold=True: Traz TUDO (Ativos e Zerados).
    Se include_sold=False: Traz apenas o que tem no estoque (Qtd > 0).
    """
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
    """Atualiza os dados. Se a quantidade voltar a ser > 0, ele 'ressuscita' no estoque."""
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
    """Diminui o estoque. Se chegar a 0, marca como vendido mas NÃO apaga."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (product_id,))
    prod = cursor.fetchone()
    
    if prod and prod['quantidade'] >= quantity_sold:
        nova_qtd = prod['quantidade'] - quantity_sold
        cursor.execute("""
            UPDATE produtos 
            SET quantidade = ?, vendido = ?, data_ultima_venda = ? 
            WHERE id = ?
        """, (nova_qtd, 1 if nova_qtd == 0 else 0, datetime.now().isoformat(), product_id))
        conn.commit()
    conn.close()

def delete_produto(product_id):
    """Remoção física (Cuidado!)."""
    conn = get_db_connection()
    conn.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
