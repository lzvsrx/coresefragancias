import streamlit as st
import os
from datetime import datetime
from utils.database import get_all_produtos, ASSETS_DIR, safe_int, safe_float

st.set_page_config(page_title="Produtos Vendidos", page_icon="💰", layout="wide")

def format_to_brl(value):
    try:
        num = safe_float(value)
        formatted = f"{num:_.2f}".replace(".", "X").replace("_", ".").replace("X", ",")
        return "R$ " + formatted
    except Exception:
        return "R$ N/A"

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

st.title("💰 Histórico de Produtos Vendidos")
st.markdown("---")
st.info("Lista de produtos que já tiveram pelo menos uma venda registrada.")

todos = get_all_produtos(include_sold=True)

# 👉 PRODUTOS QUE JÁ FORAM VENDIDOS
vendidos = [p for p in todos if p.get("data_ultima_venda")]

if not vendidos:
    st.success("Nenhum produto vendido até o momento.")
    st.stop()

total_valor = sum(safe_float(p.get("preco", 0)) for p in vendidos)

col1, col2 = st.columns(2)
with col1:
    st.metric("Produtos vendidos", len(vendidos))
with col2:
    st.metric("Somatório de preços", format_to_brl(total_valor))

st.markdown("---")

for p in vendidos:
    with st.container(border=True):
        col_info, col_img = st.columns([3, 1])

        with col_info:
            st.markdown(f"**{p.get('nome', 'N/A')}**")
            st.write(f"Preço: {format_to_brl(p.get('preco', 0))}")
            st.write(f"Quantidade atual: {safe_int(p.get('quantidade', 0))}")
            st.caption(
                f"Marca: {p.get('marca', 'N/A')} • Tipo: {p.get('tipo', 'N/A')}"
            )
            st.caption(f"Última venda: {p.get('data_ultima_venda')}")

        with col_img:
            foto = p.get("foto")
            if foto:
                path = os.path.join(ASSETS_DIR, foto)
                if os.path.exists(path):
                    st.image(path, use_container_width=True)
                else:
                    st.caption("Sem foto")
            else:
                st.caption("Sem foto")

st.markdown("---")
st.caption(f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
