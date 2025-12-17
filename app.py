# utils/database.py

import sqlite3
import os
import hashlib
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import io

# Diretórios
DATABASE_DIR = "data"
DATABASE = os.path.join(DATABASE_DIR, "estoque.db")
ASSETS_DIR = "assets"

os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Listas básicas (você pode expandir)
MARCAS = [
    "Eudora", "O Boticário", "Jequiti", "Avon", "Mary Kay",
    "Natura", "Pierre Alexander", "Tupperware", "Outra"
]

ESTILOS = [
    "Perfumaria", "Skincare", "Cabelo", "Corpo e Banho",
    "Make", "Masculinos", "Femininos", "Outro"
]

TIPOS = [
    "Perfumaria feminina", "Perfumaria masculina", "Body splash",
    "Desodorantes", "Shampoo", "Condicionador", "Outro"
]

def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default

def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
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
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", hash_password("123"), "admin")
        )
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()

create_tables()

# ---------- PRODUTOS ----------

def add_produto(nome, preco, quantidade, marca, estilo, tipo, foto=None, data_validade=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute("BEGIN")
        cursor.execute("""
            INSERT INTO produtos (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_all_produtos(include_sold: bool = True):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if include_sold:
            cursor.execute("SELECT * FROM produtos ORDER BY nome ASC")
        else:
            cursor.execute("SELECT * FROM produtos WHERE quantidade > 0 ORDER BY nome ASC")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

def get_produto_by_id(product_id: int):
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
        conn.execute("BEGIN")
        cursor.execute("""
            UPDATE produtos
            SET nome=?, preco=?, quantidade=?, marca=?, estilo=?, tipo=?, foto=?, data_validade=?
            WHERE id=?
        """, (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade, product_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def delete_produto(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute("BEGIN")
        produto = get_produto_by_id(product_id)
        if produto and produto.get("foto"):
            try:
                os.remove(os.path.join(ASSETS_DIR, produto["foto"]))
            except FileNotFoundError:
                pass
        cursor.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def mark_produto_as_sold(product_id: int, quantity_sold: int = 1):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute("BEGIN")
        produto = get_produto_by_id(product_id)
        if not produto or safe_int(produto.get("quantidade", 0)) < quantity_sold:
            raise ValueError("Estoque insuficiente!")
        cursor.execute(
            "UPDATE produtos SET quantidade = quantidade - ?, data_ultima_venda = ? WHERE id = ?",
            (quantity_sold, datetime.now().isoformat(), product_id)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# ---------- USUÁRIOS ----------

def add_user(username, password, role="staff"):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.execute("BEGIN")
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
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
    finally:
        conn.close()

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, role FROM users ORDER BY role DESC, username ASC")
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

def check_user_login(username, password):
    user = get_user(username)
    if user and user["password"] == hash_password(password):
        return user
    return None

# ---------- CSV / PDF ----------

def export_produtos_to_csv_content():
    produtos = get_all_produtos()
    if not produtos:
        return ""
    fieldnames = list(produtos[0].keys())
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore", delimiter=";")
    writer.writeheader()
    writer.writerows(produtos)
    return buffer.getvalue()

def import_produtos_from_csv_buffer(file_buffer):
    conn = get_db_connection()
    cursor = conn.cursor()
    count = 0
    try:
        conn.execute("BEGIN")
        content = file_buffer.getvalue().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content), delimiter=";")
        for row in reader:
            nome = row.get("nome")
            if not nome:
                continue
            preco = safe_float(row.get("preco", "0"))
            quantidade = safe_int(row.get("quantidade", "0"))
            cursor.execute("""
                INSERT INTO produtos (nome, preco, quantidade, marca, estilo, tipo, foto, data_validade, vendido, data_ultima_venda)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nome, preco, quantidade,
                row.get("marca"), row.get("estilo"), row.get("tipo"),
                row.get("foto"), row.get("data_validade"),
                safe_int(row.get("vendido", "0")),
                row.get("data_ultima_venda")
            ))
            count += 1
        conn.commit()
        return count
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def generate_stock_pdf_bytes():
    produtos = get_all_produtos(include_sold=False)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(cm, y, "Relatório de Estoque Ativo - Cores e Fragrâncias")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(cm, y, f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    y -= 20

    c.setFont("Helvetica-Bold", 10)
    cols = [cm, cm*6, cm*11, cm*13, cm*15, cm*17.5]
    headers = ["Nome", "Marca", "Tipo", "Qtd", "Preço", "Validade"]
    for i, h in enumerate(headers):
        c.drawString(cols[i], y, h)
    y -= 5
    c.line(cm, y, width - cm, y)
    y -= 15

    c.setFont("Helvetica", 9)
    total = 0.0
    for p in produtos:
        if y < 40:
            c.showPage()
            y = height - 50
        nome = p.get("nome", "-")[:30]
        marca = p.get("marca", "-")[:20]
        tipo = p.get("tipo", "-")[:20]
        qtd = safe_int(p.get("quantidade", 0))
        preco = safe_float(p.get("preco", 0.0))
        total += preco * qtd
        validade = p.get("data_validade") or "-"
        try:
            if validade != "-":
                validade = datetime.fromisoformat(validade).strftime("%d/%m/%Y")
        except Exception:
            pass
        preco_txt = f"R$ {preco:_.2f}".replace(".", "X").replace("_", ".").replace("X", ",")

        c.drawString(cols[0], y, nome)
        c.drawString(cols[1], y, marca)
        c.drawString(cols[2], y, tipo)
        c.drawString(cols[3], y, str(qtd))
        c.drawString(cols[4], y, preco_txt)
        c.drawString(cols[5], y, validade)
        y -= 15

    y -= 10
    total_txt = f"R$ {total:_.2f}".replace(".", "X").replace("_", ".").replace("X", ",")
    c.line(cm, y, width - cm, y)
    y -= 15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(cm, y, f"VALOR TOTAL DO ESTOQUE ATIVO: {total_txt}")
    c.save()
    buf.seek(0)
    return buf.getvalue()
