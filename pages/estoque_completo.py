import streamlit as st
import os
from utils.database import get_all_produtos, ASSETS_DIR

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(page_title="Estoque Geral", layout="wide")
load_css()

def format_brl(val):
    return f"R$ {float(val):_.2f}".replace('.', ',').replace('_', '.')

st.title("📦 Estoque Completo")

produtos = get_all_produtos(include_sold=True)
total_financeiro = 0.0

if produtos:
    for p in produtos:
        subtotal = p['quantidade'] * p['preco']
        total_financeiro += subtotal
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                img = os.path.join(ASSETS_DIR, p['foto']) if p['foto'] else ""
                if img and os.path.exists(img): st.image(img, width=100)
            with col2:
                st.subheader(p['nome'])
                st.write(f"**Qtd:** {p['quantidade']} | **Preço:** {format_brl(p['preco'])} | **Subtotal:** {format_brl(subtotal)}")
                if p['quantidade'] <= 0: st.error("Esgotado")
        st.divider()

st.sidebar.metric("Total em Estoque", format_brl(total_financeiro))
