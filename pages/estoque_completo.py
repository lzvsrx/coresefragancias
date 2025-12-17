import streamlit as st
from utils.database import get_all_produtos, ASSETS_DIR
import os

def format_to_brl(value):
    try:
        num = float(value)
        formatted = f"{num:_.2f}".replace('.', ',').replace('_', '.')
        return "R$ " + formatted
    except: return "R$ 0,00"

st.set_page_config(page_title="Estoque - Cores e Fragrâncias", layout="wide")
st.title("📦 Estoque Completo")

# include_sold=True garante que produtos com 0 unidades apareçam (com alerta)
produtos = get_all_produtos(include_sold=True)

if not produtos:
    st.info("Nenhum produto cadastrado.")
else:
    # Filtros
    marcas = sorted(list({p.get("marca") for p in produtos if p.get("marca")}))
    estilos = sorted(list({p.get("estilo") for p in produtos if p.get("estilo")}))
    
    c1, c2 = st.columns(2)
    with c1: f_marca = st.selectbox("Marca", ["Todas"] + marcas)
    with c2: f_estilo = st.selectbox("Estilo", ["Todos"] + estilos)

    filtrados = [p for p in produtos if (f_marca == "Todas" or p['marca'] == f_marca) and (f_estilo == "Todos" or p['estilo'] == f_estilo)]

    total_geral = 0.0
    for p in filtrados:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                path = os.path.join(ASSETS_DIR, p['foto']) if p['foto'] else ""
                if path and os.path.exists(path): st.image(path, width=120)
                else: st.write("📷 S/ Foto")
            with col2:
                st.subheader(p['nome'])
                qtd = p['quantidade']
                total_item = qtd * p['preco']
                total_geral += total_item
                
                if qtd <= 0:
                    st.error(f"⚠️ ESGOTADO (Quantidade: {qtd})")
                else:
                    st.write(f"**Estoque:** {qtd} un. | **Preço:** {format_to_brl(p['preco'])}")
                    st.write(f"**Total em estoque deste item:** {format_to_brl(total_item)}")
        st.divider()

    st.success(f"💰 Valor Total em Estoque (filtrado): {format_to_brl(total_geral)}")
