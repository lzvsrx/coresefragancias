import streamlit as st
from datetime import datetime
import os

# IMPORT SEGURA
try:
    from utils.database import get_all_produtos, ASSETS_DIR, MARCAS, ESTILOS, TIPOS
except:
    st.error("❌ Erro no database.py")
    st.stop()

# 🔧 FUNÇÕES SEGURAS (ANTES de serem usadas!)
def safe_int(value, default=0):
    """Converte para int com fallback."""
    try: return int(value)
    except: return default

def safe_float(value, default=0.0):
    """Converte para float com fallback."""
    try: return float(value)
    except: return default

def format_to_brl(value):
    """Formato BRL seguro."""
    try:
        num = safe_float(value)
        formatted = f"{num:_.2f}".replace('.', 'X').replace('_', '.').replace('X', ',')
        return f"R$ {formatted}"
    except: return "R$ N/A"

def format_date(date_str):
    """Formata data ISO para BR."""
    if not date_str: return 'N/A'
    try: return datetime.fromisoformat(date_str).strftime('%d/%m/%Y')
    except: return str(date_str)[:10]

# Configuração (PRIMEIRO!)
st.set_page_config(page_title="Estoque - Cores e Fragrâncias", page_icon="📦", layout="wide")

# ... resto do seu código com safe_int/safe_float funcionando ...
