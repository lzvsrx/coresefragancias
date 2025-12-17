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

# Listas oficiais conforme solicitado
MARCAS = ["Eudora", "O Boticário", "Jequiti", "Avon", "Mary Kay", "Natura", "Oui-Original-Unique-Individuel", "Pierre Alexander", "Tupperware", "Outra"]
ESTILOS = ["Perfumaria", "Skincare", "Cabelo", "Corpo e Banho", "Make", "Masculinos", "Femininos Nina Secrets", "Marcas", "Infantil", "Casa", "Solar", "Maquiage", "Teen", "Kits e Presentes", "Cuidados com o Corpo", "Lançamentos", "Acessórios de Casa", "Outro"]
TIPOS = ["Perfumaria masculina", "Perfumaria feminina", "Body splash", "Body spray", "Eau de parfum", "Desodorantes", "Perfumaria infantil", "Perfumaria vegana", "Clareador de manchas", "Anti-idade", "Protetor solar facial", "Rosto", "Tratamento para o rosto", "Acne", "Limpeza", "Esfoliante", "Tônico facial", "Kits de tratamento", "Tratamento para cabelos", "Shampoo", "Condicionador", "Leave-in e Creme para Pentear", "Finalizador", "Modelador", "Acessórios", "Kits e looks", "Boca", "Olhos", "Pincéis", "Paleta", "Unhas", "Sobrancelhas", "Kits de tratamento", "Hidratante", "Cuidados pós-banho", "Cuidados para o banho", "Barba", "Óleo corporal", "Cuidados íntimos", "Unissex", "Bronzeamento", "Protetor solar", "Depilação", "Mãos", "Lábios", "Pés", "Pós sol", "Protetor solar corporal", "Colônias", "Estojo", "Sabonetes", "Creme hidratante para as mãos", "Creme hidratante para os pés", "Miniseries", "Kits de perfumes", "Antissinais", "Máscara", "Creme bisnaga", "Roll On Fragranciado", "Roll On On Duty", "Sabonete líquido", "Sabonete em barra", "Shampoo 2 em 1", "Spray corporal", "Booster de Tratamento", "Creme para Pentear", "Óleo de Tratamento", "Pré-shampoo", "Sérum de Tratamento", "Shampoo e Condicionador", "Garrafas", "Armazenamentos", "Micro-ondas", "Servir", "Preparo", "Infantil", "Lazer/Outdoor", "Presentes", "Outro"]

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

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
    conn.commit()
    conn.close()

create_tables()

# --- FUNÇÕES DE LEITURA E REPOSIÇÃO ---

def get_all_produtos(include_sold=True):
    """Lê o banco de dados. Se include_sold=True, traz os itens 'sumidos' (zerados)."""
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
    """Atualiza e garante que o item volte a aparecer se a quantidade for > 0."""
    conn = get_db_connection()
    conn.execute("""
        UPDATE produtos SET nome=?, preco=?, quantidade=?, marca=?, estilo=?, tipo=?, foto=?, data_validade=?
        WHERE id=?
    """, (nome, preco, qtd, marca, estilo, tipo, foto, validade, p_id))
    conn.commit()
    conn.close()

def mark_produto_as_sold(product_id, quantity_sold=1):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if row and row['quantidade'] >= quantity_sold:
        nova_qtd = row['quantidade'] - quantity_sold
        cursor.execute("""
            UPDATE produtos SET quantidade = ?, vendido = ?, data_ultima_venda = ? 
            WHERE id = ?
        """, (nova_qtd, 1 if nova_qtd == 0 else 0, datetime.now().isoformat(), product_id))
        conn.commit()
    conn.close()
