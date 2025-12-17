import streamlit as st
import os
from datetime import datetime
from utils.database import get_all_produtos, ASSETS_DIR, safe_int, safe_float

st.set_page_config(page_title="Produtos Esgotados", page_icon="💰", layout="wide")

def format_to_brl(value):
    try:
        num = safe_float(value)
        formatted = f"{num:_.2f}".replace(".", "X").replace("_", ".").replace("X", ",")
        return "R$ " + formatted
    except Exception:
        return "R$ N/A"

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        try:
            with open(file_name, encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception:
            pass

load_css("style.css")

st.title("💰 Histórico de Itens Esgotados")
st.markdown("---")
st.info("Produtos com quantidade igual a zero (esgotados).")

todos = get_all_produtos(include_sold=True)
esgotados = [p for p in todos if safe_int(p.get("quantidade", 0)) == 0]

if not esgotados:
    st.success("Nenhum produto esgotado no momento.")
    st.stop()

total_valor = 0.0
for p in esgotados:
    total_valor += safe_float(p.get("preco", 0))

col1, col2 = st.columns(2)
with col1:
    st.metric("Itens esgotados", len(esgotados))
with col2:
    st.metric("Somatório de preços", format_to_brl(total_valor))

st.markdown("---")

for p in esgotados:
    with st.container(border=True):
        col_info, col_img = st.columns([3, 1])
        with col_info:
            st.markdown(f"**{p.get('nome', 'N/A')}**")
            st.write(f"Preço unitário: {format_to_brl(p.get('preco', 0))}")
            st.caption(f"Marca: {p.get('marca', 'N/A')} • Tipo: {p.get('tipo', 'N/A')}")
            if p.get("data_ultima_venda"):
                st.caption(f"Última venda: {p['data_ultima_venda']}")
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
