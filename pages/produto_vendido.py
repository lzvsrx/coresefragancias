import streamlit as st
import os
from utils.database import get_all_produtos

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(page_title="Vendas")
load_css()

st.title("💰 Produtos Vendidos")

vendidos = [p for p in get_all_produtos(include_sold=True) if p['quantidade'] <= 0 and p['vendido'] == 1]
total_vendido = sum(p['preco'] for p in vendidos)

if vendidos:
    for p in vendidos:
        st.success(f"**{p['nome']}** - Vendido por R$ {p['preco']:.2f}")
    st.divider()
    st.metric("Total Acumulado (Esgotados)", f"R$ {total_vendido:,.2f}")
else:
    st.info("Sem vendas registradas.")
