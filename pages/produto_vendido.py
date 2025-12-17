import streamlit as st
from utils.database import get_all_produtos
from datetime import datetime

st.title("💰 Produtos Vendidos")
st.info("Produtos com estoque zerado.")

produtos = get_all_produtos(include_sold=True)
vendidos = [p for p in produtos if p.get("quantidade", 0) <= 0]

if not vendidos:
    st.success("Nenhum produto esgotado!")
else:
    for p in vendidos:
        st.write(f"### {p.get('nome')}")
        st.write(f"Marca: {p.get('marca')} | Última Venda: {p.get('data_ultima_venda') or 'N/A'}")
        st.divider()
