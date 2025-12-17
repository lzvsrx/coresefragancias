import streamlit as st
import os
from utils.database import get_all_produtos

st.set_page_config(page_title="Vendas")
if os.path.exists("style.css"):
    with open("style.css", encoding='utf-8') as f: st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("💰 Produtos Vendidos (Esgotados)")

vendidos = [p for p in get_all_produtos(include_sold=True) if p['quantidade'] <= 0 and p['vendido'] == 1]
total_vendas = sum(p['preco'] for p in vendidos)

for p in vendidos:
    st.write(f"✅ **{p['nome']}** - Vendido por: R$ {p['preco']:.2f}")

st.sidebar.metric("Total Vendido", f"R$ {total_vendas:,.2f}")
