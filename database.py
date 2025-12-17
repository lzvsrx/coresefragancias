import sqlite3
import os
import hashlib
import shutil
from datetime import datetime

DATABASE_DIR = "data"
BACKUP_DIR = os.path.join(DATABASE_DIR, "backups")
DATABASE = os.path.join(DATABASE_DIR, "estoque.db")
ASSETS_DIR = "assets"

os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

def realizar_backup():
    if os.path.exists(DATABASE):
        data_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"estoque_backup_{data_str}.db")
        shutil.copy2(DATABASE, backup_path)
        backups = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)])
        if len(backups) > 10: os.remove(backups[0])

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    realizar_backup()
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
    conn.commit()
    conn.close()

create_tables()

def get_all_produtos(include_sold=True):
    conn = get_db_connection()
    cursor = conn.cursor()
    if include_sold:
        cursor.execute("SELECT * FROM produtos ORDER BY nome ASC")
    else:
        cursor.execute("SELECT * FROM produtos WHERE quantidade > 0 ORDER BY nome ASC")
    produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return produtos

def update_produto(p_id, nome, preco, qtd, marca, estilo, tipo, foto, validade):
    conn = get_db_connection()
    conn.execute("""
        UPDATE produtos SET nome=?, preco=?, quantidade=?, marca=?, estilo=?, tipo=?, foto=?, data_validade=?
        WHERE id=?
    """, (nome, preco, qtd, marca, estilo, tipo, foto, validade, p_id))
    conn.commit()
    conn.close()
