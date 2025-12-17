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

# Listas Oficiais Fornecidas
MARCAS = ["Eudora", "O Boticário", "Jequiti", "Avon", "Mary Kay", "Natura", "Oui-Original-Unique-Individuel", "Pierre Alexander", "Tupperware", "Outra"]
ESTILOS = ["Perfumaria", "Skincare", "Cabelo", "Corpo e Banho", "Make", "Masculinos", "Femininos Nina Secrets", "Marcas", "Infantil", "Casa", "Solar", "Maquiage", "Teen", "Kits e Presentes", "Cuidados com o Corpo", "Lançamentos", "Acessórios de Casa", "Outro"]
TIPOS = ["Perfumaria masculina", "Perfumaria feminina", "Body splash", "Body spray", "Eau de parfum", "Desodorantes", "Perfumaria infantil", "Perfumaria vegana", "Clareador de manchas", "Anti-idade", "Protetor solar facial", "Rosto", "Tratamento para o rosto", "Acne", "Limpeza", "Esfoliante", "Tônico facial", "Kits de tratamento", "Tratamento para cabelos", "Shampoo", "Condicionador", "Leave-in e Creme para Pentear", "Finalizador", "Modelador", "Acessórios", "Kits e looks", "Boca", "Olhos", "Pincéis", "Paleta", "Unhas", "Sobrancelhas", "Hidratante", "Cuidados pós-banho", "Cuidados para o banho", "Barba", "Óleo corporal", "Cuidados íntimos", "Unissex", "Bronzeamento", "Protetor solar", "Depilação", "Mãos", "Lábios", "Pés", "Pós sol", "Protetor solar corporal", "Colônias", "Estojo", "Sabonetes", "Creme hidratante para as mãos", "Creme hidratante para os pés", "Miniseries", "Kits de perfumes", "Antissinais", "Máscara", "Creme bisnaga", "Roll On Fragranciado", "Roll On On Duty", "Sabonete líquido", "Sabonete em barra", "Shampoo 2 em 1", "Spray corporal", "Booster de Tratamento", "Creme para Pentear", "Óleo de Tratamento", "Pré-shampoo", "Sérum de Tratamento", "Shampoo e Condicionador", "Garrafas", "Armazenamentos", "Micro-ondas", "Servir", "Preparo", "Infantil", "Lazer/Outdoor", "Presentes", "Outro"]

def realizar_backup():
    if os.path.exists(DATABASE):
        data_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{data_str}.db")
        shutil.copy2(DATABASE, backup_path)
        backups = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)])
        if len(backups) > 5: os.remove(backups[0])

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    realizar_backup()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL, preco REAL NOT NULL, quantidade INTEGER NOT NULL,
            marca TEXT, estilo TEXT, tipo TEXT, foto TEXT, data_validade TEXT,
            vendido INTEGER DEFAULT 0, data_ultima_venda TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE, password TEXT NOT NULL, role TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

create_tables()

# --- Funções de Produto ---
def get_all_produtos(include_sold=True):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM produtos ORDER BY nome ASC" if include_sold else "SELECT * FROM produtos WHERE quantidade > 0 ORDER BY nome ASC"
    cursor.execute(query)
    res = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return res

def update_produto(p_id, nome, preco, qtd, marca, estilo, tipo, foto, validade):
    conn = get_db_connection()
    conn.execute("UPDATE produtos SET nome=?, preco=?, quantidade=?, marca=?, estilo=?, tipo=?, foto=?, data_validade=? WHERE id=?", 
                 (nome, preco, qtd, marca, estilo, tipo, foto, validade, p_id))
    conn.commit()
    conn.close()

# --- Funções de Usuário ---
def get_user(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def add_user(username, password, role="staff"):
    conn = get_db_connection()
    hashed = hash_password(password)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed, role))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_db_connection()
    users = conn.execute("SELECT username, role FROM users").fetchall()
    conn.close()
    return [dict(u) for u in users]

def delete_user(username):
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
