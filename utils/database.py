# ====================================================================
# utils/database.py - BANCO DE DADOS CORRIGIDO (CAPACIDADE INFINITA)
# ====================================================================

import sqlite3
import os
import hashlib
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime, date
import io

# ====================================================================
# CONFIGURAÇÃO DE DIRETÓRIOS
# ====================================================================
DATABASE_DIR = "data"
DATABASE = os.path.join(DATABASE_DIR, "estoque.db")
ASSETS_DIR = "assets"

if not os.path.exists(DATABASE_DIR): os.makedirs(DATABASE_DIR)
if not os.path.exists(ASSETS_DIR): os.makedirs(ASSETS_DIR)

# CATEGORIAS (EXPORTADAS)
MARCAS = ["Eudora", "O Boticário", "Jequiti", "Avon", "Mary Kay", "Natura", "Tupperware", "Outra"]
ESTILOS = ["Perfumaria", "Skincare", "Cabelo", "Corpo e Banho", "Make", "Outro"]
TIPOS = ["Perfumaria feminina", "Perfumaria masculina", "Body splash", "Desodorantes", "Shampoo", "Outro"]

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # TABELA PRODUTOS (INFINITA via AUTOINCREMENT)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL,
        quantidade INTEGER NOT NULL,
        marca TEXT, estilo TEXT, tipo TEXT, foto TEXT,
        data_validade TEXT, vendido INTEGER DEFAULT 0,
        data_ultima_venda TEXT
    )
    """)
    
    # TABELA USUÁRIOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)
    
    # USUÁRIO ADMIN PADRÃO
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", 
                      ("admin", hash_password("123"), "admin"))
    except sqlite3.IntegrityError: pass
    
    conn.commit()
    conn.close()

create_tables()  # Inicializa

# ====================================================================
# CRUD PRODUTOS (TRANSÇÕES SEGURAS)
# ====================================================================
def add_produto(nome, preco, quantidade, marca, estilo, tipo, foto=None, data_validade=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute('BEGIN')
        cursor.execute("""
            INSERT INTO produtos (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_produtos(include_sold=True):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if include_sold:
            cursor.execute("SELECT * FROM produtos ORDER BY nome ASC")
        else:
            cursor.execute("SELECT * FROM produtos WHERE quantidade > 0 ORDER BY nome ASC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_produto_by_id(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def update_produto(product_id, nome, preco, quantidade, marca, estilo, tipo, foto, data_validade):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute('BEGIN')
        cursor.execute("""
            UPDATE produtos SET nome=?, preco=?, quantidade=?, marca=?, estilo=?, tipo=?, foto=?, data_validade=?
            WHERE id=?
        """, (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade, product_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_produto(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute('BEGIN')
        produto = get_produto_by_id(product_id)
        if produto and produto.get('foto'):
            try: os.remove(os.path.join(ASSETS_DIR, produto['foto']))
            except: pass
        cursor.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def mark_produto_as_sold(product_id, quantity_sold=1):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute('BEGIN')
        produto = get_produto_by_id(product_id)
        if not produto or safe_int(produto.get('quantidade', 0)) < quantity_sold:
            raise ValueError("Estoque insuficiente!")
        cursor.execute("""
            UPDATE produtos SET quantidade = quantidade - ?, data_ultima_venda = ? WHERE id = ?
        """, (quantity_sold, datetime.now().isoformat(), product_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# USUÁRIOS
def add_user(username, password, role="staff"):
    hashed = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute('BEGIN')
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                      (username, hashed, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
