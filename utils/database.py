# ====================================================================
# ARQUIVO: utils/database.py
# Contém as funções de DB (SQLite), Hash, CRUD, Login e Exportação.
# ====================================================================

import sqlite3
import os
import hashlib
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import io

# ====================================================================
# CONFIGURAÇÃO DE DIRETÓRIOS E CONSTANTES
# ====================================================================

DATABASE_DIR = "data"
DATABASE = os.path.join(DATABASE_DIR, "estoque.db")
ASSETS_DIR = "assets"

# Assegura que os diretórios existam
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Listas de Categorias (Sincronizadas com o Front-end)
MARCAS = [
    "Eudora", "O Boticário", "Jequiti", "Avon", "Mary Kay", "Natura",
    "Oui-Original-Unique-Individuel", "Pierre Alexander", "Tupperware", "Outra"
]
ESTILOS = [
    "Perfumaria", "Skincare", "Cabelo", "Corpo e Banho", "Make", "Masculinos", 
    "Femininos Nina Secrets", "Marcas", "Infantil", "Casa", "Solar", "Maquiage", 
    "Teen", "Kits e Presentes", "Cuidados com o Corpo", "Lançamentos", 
    "Acessórios de Casa", "Outro"
]
TIPOS = [
    "Perfumaria masculina", "Perfumaria feminina", "Body splash", "Body spray", 
    "Eau de parfum", "Desodorantes", "Perfumaria infantil", "Perfumaria vegana", 
    "Familia olfativa", "Clareador de manchas", "Anti-idade", "Protetor solar facial", 
    "Rosto", "Tratamento para o rosto", "Acne", "Limpeza", "Esfoliante", "Tônico facial",
    "Kits de tratamento", "Tratamento para cabelos", "Shampoo", "Condicionador",
    "Leave-in e Creme para Pentear", "Finalizador", "Modelador", "Acessórios",
    "Kits e looks", "Boca", "Olhos", "Pincéis", "Paleta", "Unhas", "Sobrancelhas",
    "Hidratante", "Cuidados pós-banho", "Cuidados para o banho", "Barba", 
    "Óleo corporal", "Cuidados íntimos", "Unissex", "Bronzeamento", "Protetor solar", 
    "Depilação", "Mãos", "Lábios", "Pés", "Pós sol", "Protetor solar corporal", 
    "Colônias", "Estojo", "Sabonetes", "Creme hidratante para as mãos", 
    "Creme hidratante para os pés", "Miniseries", "Kits de perfumes", "Antissinais", 
    "Máscara", "Creme bisnaga", "Roll On Fragranciado", "Roll On On Duty", 
    "Sabonete líquido", "Sabonete em barra", "Shampoo 2 em 1", "Spray corporal", 
    "Booster de Tratamento", "Creme para Pentear", "Óleo de Tratamento", "Pré-shampoo",
    "Sérum de Tratamento", "Shampoo e Condicionador", "Garrafas", "Armazenamentos", 
    "Micro-ondas", "Servir", "Preparo", "Infantil", "Lazer/Outdoor", "Presentes", "Outro"
]

# ====================================================================
# FUNÇÕES DE UTILIDADE E CONEXÃO
# ====================================================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Gera o hash SHA256 da senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    """Inicializa as tabelas e o usuário admin padrão."""
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
    
    # Criar admin padrão (Senha: 123)
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("admin", hash_password("123"), "admin"))
    except sqlite3.IntegrityError:
        pass 

    conn.commit()
    conn.close()

# Inicialização automática
create_tables()

# ====================================================================
# GESTÃO DE PRODUTOS (CRUD)
# ====================================================================

def add_produto(nome, preco, quantidade, marca, estilo, tipo, foto=None, data_validade=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade)
    )
    conn.commit()
    conn.close()

def get_all_produtos(include_out_of_stock=True):
    """Retorna produtos ordenados. Se include_out_of_stock=False, filtra apenas disponíveis."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if include_out_of_stock:
        cursor.execute("SELECT * FROM produtos ORDER BY nome ASC")
    else:
        cursor.execute("SELECT * FROM produtos WHERE quantidade > 0 ORDER BY nome ASC")
    produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return produtos

def get_produtos_vendidos():
    """Histórico de itens com flag de vendido ou estoque zerado."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE vendido = 1 ORDER BY data_ultima_venda DESC")
    produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return produtos

def get_produto_by_id(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (product_id,))
    produto = cursor.fetchone()
    conn.close()
    return dict(produto) if produto else None

def update_produto(product_id, nome, preco, quantidade, marca, estilo, tipo, foto, data_validade):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produtos SET nome=?, preco=?, quantidade=?, marca=?, estilo=?, tipo=?, foto=?, data_validade=?
        WHERE id=?
    """, (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade, product_id))
    conn.commit()
    conn.close()

def delete_produto(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Limpa a foto física se existir
    produto = get_produto_by_id(product_id)
    if produto and produto.get('foto'):
        try:
            os.remove(os.path.join(ASSETS_DIR, produto['foto']))
        except: pass
    cursor.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def mark_produto_as_sold(product_id, quantity_sold=1):
    """Deduz quantidade e marca como vendido para histórico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    produto = get_produto_by_id(product_id)
    if not produto or produto['quantidade'] < quantity_sold:
        raise ValueError("Quantidade em estoque insuficiente.")
    
    cursor.execute(
        "UPDATE produtos SET quantidade = quantidade - ?, vendido = 1, data_ultima_venda = ? WHERE id = ?",
        (quantity_sold, datetime.now().isoformat(), product_id)
    )
    conn.commit()
    conn.close()

# ====================================================================
# GESTÃO DE USUÁRIOS E SEGURANÇA
# ====================================================================

def add_user(username, password, role="staff"):
    hashed_pass = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hashed_pass, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError: return False
    finally: conn.close()

def get_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users ORDER BY role DESC")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

# ====================================================================
# EXPORTAÇÃO E IMPORTAÇÃO
# ====================================================================

def export_produtos_to_csv_content():
    produtos = get_all_produtos()
    if not produtos: return ""
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=produtos[0].keys(), delimiter=';')
    writer.writeheader()
    writer.writerows(produtos)
    return csv_buffer.getvalue()

def import_produtos_from_csv_buffer(file_buffer):
    conn = get_db_connection()
    cursor = conn.cursor()
    count = 0
    string_data = io.StringIO(file_buffer.getvalue().decode('utf-8'))
    reader = csv.DictReader(string_data, delimiter=';')
    
    for row in reader:
        try:
            cursor.execute("""
                INSERT INTO produtos (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (row['nome'], float(row['preco'].replace(',', '.')), int(row['quantidade']), 
                  row.get('marca'), row.get('estilo'), row.get('tipo'), None, row.get('data_validade')))
            count += 1
        except: continue
    conn.commit()
    conn.close()
    return count

def generate_stock_pdf_bytes():
    """Gera relatório em PDF formatado."""
    produtos = get_all_produtos(include_out_of_stock=False)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont('Helvetica-Bold', 14)
    c.drawString(cm, y, "Relatório de Estoque - Cores e Fragrâncias")
    y -= 30

    # Cabeçalho Tabela
    c.setFont('Helvetica-Bold', 10)
    c.drawString(cm, y, "Produto")
    c.drawString(cm*10, y, "Marca")
    c.drawString(cm*14, y, "Qtd")
    c.drawString(cm*16, y, "Preço")
    y -= 5
    c.line(cm, y, width-cm, y)
    y -= 15

    c.setFont('Helvetica', 9)
    for p in produtos:
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(cm, y, str(p['nome'])[:40])
        c.drawString(cm*10, y, str(p['marca']))
        c.drawString(cm*14, y, str(p['quantidade']))
        c.drawString(cm*16, y, f"R$ {p['preco']:.2f}")
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
