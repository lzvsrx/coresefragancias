import streamlit as st
from utils.database import get_all_produtos
import os

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

st.title("💰 Produtos Vendidos (Zerados)")

# Filtra apenas o que está zerado mas já foi vendido no passado
vendidos = [p for p in get_all_produtos(include_sold=True) if p['quantidade'] <= 0 and p['vendido'] == 1]

if not vendidos:
    st.info("Nenhum item vendido no histórico.")
else:
    for p in vendidos:
        st.write(f"### {p['nome']}")
        st.write(f"Vendido em: {p['data_ultima_venda'] or 'Data não registrada'}")
        st.divider()
