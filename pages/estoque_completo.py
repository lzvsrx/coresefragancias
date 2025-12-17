import streamlit as st
from utils.database import get_all_produtos, ASSETS_DIR
import os

def format_to_brl(value):
    try:
        return f"R$ {float(value):_.2f}".replace('.', ',').replace('_', '.')
    except: return "R$ N/A"

st.title("📦 Estoque Geral")

# Puxa tudo do banco, inclusive os zerados
produtos = get_all_produtos(include_sold=True)

if not produtos:
    st.info("Estoque vazio.")
else:
    # Filtros em colunas conforme seu código inicial
    c1, c2, c3 = st.columns(3)
    marcas = sorted(list({p.get("marca") for p in produtos if p.get("marca")}))
    with c1: f_marca = st.selectbox("Marca", ["Todas"] + marcas)

    prod_filtrados = [p for p in produtos if (f_marca == "Todas" or p.get("marca") == f_marca)]

    for p in prod_filtrados:
        with st.container():
            col_img, col_txt = st.columns([1, 4])
            with col_img:
                img_path = os.path.join(ASSETS_DIR, p['foto']) if p['foto'] else ""
                if img_path and os.path.exists(img_path):
                    st.image(img_path, width=100)
                else: st.write("🖼️")
            with col_txt:
                st.write(f"### {p['nome']}")
                qtd = p['quantidade']
                if qtd <= 0:
                    st.error(f"ITEM ESGOTADO/VENDIDO (Quantidade: {qtd})")
                else:
                    st.success(f"Estoque: {qtd} unidades")
                st.write(f"Preço: {format_to_brl(p['preco'])} | Validade: {p['data_validade'] or 'N/A'}")
        st.divider()
