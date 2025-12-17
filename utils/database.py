Códigos Completos Corrigidos
Aqui estão os três arquivos completos e corrigidos para resolver o problema dos produtos que somem e garantir capacidade infinita.

database.py (Completo - Correções Aplicadas)
python
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
from datetime import datetime, date
import io  # Necessário para o download de PDF e CSV no Streamlit

# ====================================================================
# CONFIGURAÇÃO DE DIRETÓRIOS E CONSTANTES
# ====================================================================

DATABASE_DIR = "data"
DATABASE = os.path.join(DATABASE_DIR, "estoque.db")
ASSETS_DIR = "assets"

# Assegura que os diretórios existam
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# Listas de categorias
MARCAS = [
    "Eudora", "O Boticário", "Jequiti", "Avon", "Mary Kay", "Natura",
    "Oui-Original-Unique-Individuel", "Pierre Alexander", "Tupperware", "Outra"
]

ESTILOS = [
    "Perfumaria", "Skincare", "Cabelo", "Corpo e Banho", "Make", "Masculinos", "Femininos Nina Secrets",
    "Marcas", "Infantil", "Casa", "Solar", "Maquiage", "Teen", "Kits e Presentes",
    "Cuidados com o Corpo", "Lançamentos", "Acessórios de Casa", "Outro"
]

TIPOS = [
    "Perfumaria masculina", "Perfumaria feminina", "Body splash", "Body spray", "Eau de parfum",
    "Desodorantes", "Perfumaria infantil", "Perfumaria vegana", "Familia olfativa",
    "Clareador de manchas", "Anti-idade", "Protetor solar facial", "Rosto",
    "Tratamento para o rosto", "Acne", "Limpeza", "Esfoliante", "Tônico facial",
    "Kits de tratamento", "Tratamento para cabelos", "Shampoo", "Condicionador",
    "Leave-in e Creme para Pentear", "Finalizador", "Modelador", "Acessórios",
    "Kits e looks", "Boca", "Olhos", "Pincéis", "Paleta", "Unhas", "Sobrancelhas",
    "Kits de tratamento", "Hidratante", "Cuidados pós-banho", "Cuidados para o banho",
    "Barba", "Óleo corporal", "Cuidados íntimos", "Unissex", "Bronzeamento",
    "Protetor solar", "Depilação", "Mãos", "Lábios", "Pés", "Pós sol",
    "Protetor solar corporal", "Colônias", "Estojo", "Sabonetes",
    "Creme hidratante para as mãos", "Creme hidratante para os pés", "Miniseries",
    "Kits de perfumes", "Antissinais", "Máscara", "Creme bisnaga",
    "Roll On Fragranciado", "Roll On On Duty", "Sabonete líquido",
    "Sabonete em barra", "Shampoo 2 em 1", "Spray corporal", "Booster de Tratamento",
    "Creme para Pentear", "Óleo de Tratamento", "Pré-shampoo",
    "Sérum de Tratamento", "Shampoo e Condicionador",
    "Garrafas", "Armazenamentos", "Micro-ondas", "Servir", "Preparo",
    "Infantil", "Lazer/Outdoor", "Presentes", "Outro"
]

# ====================================================================
# FUNÇÕES DE UTILIDADE E CONEXÃO
# ====================================================================

def get_db_connection():
    """Retorna um objeto de conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Gera o hash SHA256 da senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    """Cria as tabelas 'produtos' e 'users' se não existirem, e cria um usuário 'admin' padrão."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Cria a tabela 'produtos'
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
    
    # 2. Cria a tabela 'users'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    );
    """)
    
    # 3. Cria um usuário admin padrão se ele não existir (Senha: "123")
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ("admin", hash_password("123"), "admin"))
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()

# Garante que as tabelas sejam criadas na inicialização
create_tables()

# ====================================================================
# FUNÇÕES CRUD DE PRODUTOS (CORRIGIDAS COM TRANSações)
# ====================================================================

def add_produto(nome, preco, quantidade, marca, estilo, tipo, foto=None, data_validade=None):
    """Adiciona um novo produto ao DB com transação segura."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute('BEGIN')  # Inicia transação explícita
        cursor.execute(
            "INSERT INTO produtos (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade)
        )
        conn.commit()
        return cursor.lastrowid  # Retorna o ID do produto criado
    except Exception as e:
        conn.rollback()
        print(f"Erro ao adicionar produto: {e}")
        raise
    finally:
        conn.close()

def get_all_produtos(include_sold=True):
    """Retorna todos os produtos cadastrados (CORRIGIDO - sem consultas duplicadas)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if include_sold:
            cursor.execute("SELECT * FROM produtos ORDER BY nome ASC")
        else:
            cursor.execute("SELECT * FROM produtos WHERE quantidade > 0 ORDER BY nome ASC")
        produtos = [dict(row) for row in cursor.fetchall()]
        return produtos
    finally:
        conn.close()

def get_produtos_vendidos():
    """Retorna todos os produtos que foram marcados como vendidos (vendido=1)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM produtos WHERE vendido = 1 ORDER BY data_ultima_venda DESC")
        produtos = [dict(row) for row in cursor.fetchall()]
        return produtos
    finally:
        conn.close()

def get_produto_by_id(product_id):
    """Busca um produto pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (product_id,))
        produto = cursor.fetchone()
        return dict(produto) if produto else None
    finally:
        conn.close()

def update_produto(product_id, nome, preco, quantidade, marca, estilo, tipo, foto, data_validade):
    """Atualiza um produto existente com transação segura."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute('BEGIN')
        cursor.execute(
            """
            UPDATE produtos SET nome=?, preco=?, quantidade=?, marca=?, estilo=?, tipo=?, foto=?, data_validade=?
            WHERE id=?
            """,
            (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade, product_id)
        )
        conn.commit()
        return cursor.rowcount > 0  # Retorna True se atualizou
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar produto: {e}")
        raise
    finally:
        conn.close()

def delete_produto(product_id):
    """Remove um produto e sua foto associada com transação segura."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute('BEGIN')
        # 1. Recupera o produto para apagar a foto
        produto = get_produto_by_id(product_id)
        if produto and produto.get('foto'):
            try:
                os.remove(os.path.join(ASSETS_DIR, produto['foto']))
            except FileNotFoundError:
                pass
        
        # 2. Deleta do banco de dados
        cursor.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Erro ao deletar produto: {e}")
        raise
    finally:
        conn.close()

def mark_produto_as_sold(product_id, quantity_sold=1):
    """Marca produto como vendido com transação segura."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute('BEGIN')
        produto = get_produto_by_id(product_id)
        if not produto or produto.get('quantidade', 0) < quantity_sold:
            raise ValueError("Estoque insuficiente!")
        
        cursor.execute(
            "UPDATE produtos SET quantidade = quantidade - ?, data_ultima_venda = ? WHERE id = ?",
            (quantity_sold, datetime.now().isoformat(), product_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

# ====================================================================
# FUNÇÕES DE USUÁRIOS (LOGIN/ADMIN)
# ====================================================================

def add_user(username, password, role="staff"):
    """Adiciona um novo usuário (admin ou staff) ao banco de dados."""
    hashed_pass = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute('BEGIN')
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_pass, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    """Busca um usuário pelo nome de usuário."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def get_all_users():
    """Retorna todos os usuários cadastrados (sem senhas)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, role FROM users ORDER BY role DESC, username ASC")
        users = [dict(row) for row in cursor.fetchall()]
        return users
    finally:
        conn.close()

def check_user_login(username, password):
    """Verifica as credenciais do usuário e retorna seus dados (ou None)."""
    user = get_user(username)
    if user and user['password'] == hash_password(password):
        return user
    return None

# ====================================================================
# FUNÇÕES DE EXPORTAÇÃO/IMPORTAÇÃO (CSV/PDF)
# ====================================================================

def export_produtos_to_csv_content():
    """Exporta todos os produtos para uma string CSV (para download direto)."""
    produtos = get_all_produtos()
    if not produtos:
        return ""
    
    fieldnames = list(produtos[0].keys())
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, extrasaction='ignore', delimiter=';')
    writer.writeheader()
    writer.writerows(produtos)
    return csv_buffer.getvalue()

def import_produtos_from_csv_buffer(file_buffer):
    """Importa produtos de um buffer de arquivo CSV (substituindo o uso de filepath)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    count = 0
    try:
        conn.execute('BEGIN')
        string_data = io.StringIO(file_buffer.getvalue().decode('utf-8'))
        reader = csv.DictReader(string_data, delimiter=';')
        
        for row in reader:
            try:
                nome = row.get('nome')
                if not nome: continue
                
                preco = float(row.get('preco', '0').replace(',', '.'))
                quantidade = int(row.get('quantidade', '0'))
                vendido = int(row.get('vendido', '0'))
                
                cursor.execute(
                    """
                    INSERT INTO produtos (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade, vendido, data_ultima_venda)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (nome, preco, quantidade, row.get('marca'), row.get('estilo'),
                     row.get('tipo'), row.get('foto'), row.get('data_validade'), vendido,
                     row.get('data_ultima_venda'))
                )
                count += 1
            except ValueError:
                continue
        conn.commit()
        return count
    except Exception as e:
        conn.rollback()
        print(f"Erro ao importar CSV: {e}")
        raise
    finally:
        conn.close()

def generate_stock_pdf_bytes():
    """Gera um relatório PDF com a lista de produtos e retorna os bytes (para download direto)."""
    produtos = get_all_produtos(include_sold=False)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y_position = height - 50
    
    # Título
    c.setFont('Helvetica-Bold', 16)
    c.drawString(cm, y_position, 'Relatório de Estoque Ativo - Cores e Fragrâncias')
    y_position -= 20
    
    # Data de Geração
    c.setFont('Helvetica', 10)
    c.drawString(cm, y_position, f'Data de Geração: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    y_position -= 20
    
    # Cabeçalho da tabela
    c.setFont('Helvetica-Bold', 10)
    col_x = [cm, cm*6, cm*11, cm*13, cm*15, cm*17.5]
    c.drawString(col_x[0], y_position, 'Nome')
    c.drawString(col_x[1], y_position, 'Marca')
    c.drawString(col_x[2], y_position, 'Tipo')
    c.drawString(col_x[3], y_position, 'Qtd')
    c.drawString(col_x[4], y_position, 'Preço')
    c.drawString(col_x[5], y_position, 'Validade')
    y_position -= 5
    c.line(cm, y_position, width - cm, y_position)
    y_position -= 15
    
    # Conteúdo da tabela
    c.setFont('Helvetica', 9)
    total_valor_estoque = 0.0
    
    for p in produtos:
        if y_position < 40:
            c.showPage()
            y_position = height - 50
            # Repete o cabeçalho
            c.setFont('Helvetica-Bold', 10)
            c.drawString(col_x[0], y_position, 'Nome')
            c.drawString(col_x[1], y_position, 'Marca')
            c.drawString(col_x[2], y_position, 'Tipo')
            c.drawString(col_x[3], y_position, 'Qtd')
            c.drawString(col_x[4], y_position, 'Preço')
            c.drawString(col_x[5], y_position, 'Validade')
            y_position -= 5
            c.line(cm, y_position, width - cm, y_position)
            y_position -= 15
            c.setFont('Helvetica', 9)
        
        # Formatação de Data, Preço e Cálculo
        validade = p.get('data_validade') or '-'
        if validade != '-':
            try:
                validade = datetime.fromisoformat(validade).strftime('%d/%m/%Y')
            except ValueError:
                pass
        
        nome = p.get('nome') or '-'
        marca = p.get('marca') or '-'
        tipo = p.get('tipo') or '-'
        quantidade = p.get('quantidade') or 0
        preco = p.get('preco') or 0.0
        
        # Formato BRL para exibição
        preco_formatado = f"R$ {float(preco):_.2f}".replace('.', 'X').replace('_', '.').replace('X', ',')
        total_valor_estoque += float(preco) * float(quantidade)
        
        # Desenha as linhas
        c.drawString(col_x[0], y_position, nome[:30])
        c.drawString(col_x[1], y_position, marca[:20])
        c.drawString(col_x[2], y_position, tipo[:20])
        c.drawString(col_x[3], y_position, str(quantidade))
        c.drawString(col_x[4], y_position, preco_formatado)
        c.drawString(col_x[5], y_position, validade)
        y_position -= 15
    
    # Total de Estoque
    y_position -= 10
    total_valor_estoque_exibicao = f"R$ {total_valor_estoque:_.2f}".replace('.', 'X').replace('_', '.').replace('X', ',')
    c.line(cm, y_position, width - cm, y_position)
    y_position -= 15
    c.setFont('Helvetica-Bold', 12)
    c.drawString(col_x[0], y_position, f"VALOR TOTAL DO ESTOQUE ATIVO: {total_valor_estoque_exibicao}")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
