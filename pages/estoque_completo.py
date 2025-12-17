import streamlit as st
from utils.database import *

st.set_page_config(page_title="Estoque", page_icon="📦", layout="wide")

def safe_int(v, d=0): return int(v) if v else d
def safe_float(v, d=0.0): return float(v) if v else d
def format_to_brl(v):
    try: return f"R$ {safe_float(v):_.2f}".replace('.', 'X').replace('_', '.').replace('X', ',')
    except: return "R$ 0,00"

load_css()
st.title("📦 Estoque Completo")

produtos = get_all_produtos(include_sold=True)
if not produtos: st.info("Nenhum produto"); st.stop()

# FILTROS
col1, col2, col3 = st.columns(3)
marca_f = col1.selectbox("Marca", ["Todas"] + MARCAS)
tipo_f = col2.selectbox("Tipo", ["Todos"] + TIPOS)
qtd_min = col3.number_input("Qtd mínima", 0)

produtos = [p for p in produtos 
           if (not marca_f or marca_f == p.get('marca')) 
           and safe_int(p.get('quantidade')) >= qtd_min]

col1, col2 = st.columns(2)
col1.metric("Total itens", len(produtos))
total_valor = sum(safe_float(p['preco']) * safe_int(p['quantidade']) for p in produtos)
col2.metric("Valor total", format_to_brl(total_valor))

for p in produtos:
    with st.container(border=True):
        st.write(f"**{p['nome']}** - {p.get('marca', 'N/A')}")
        st.caption(f"R${p['preco']} | Qtd: {p['quantidade']}")
