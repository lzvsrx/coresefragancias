import streamlit as st
import os
from utils.database import get_all_produtos, update_produto

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(page_title="Recuperação")
load_css()

st.title("🔄 Recuperação")

itens = [p for p in get_all_produtos(include_sold=True) if p['quantidade'] <= 0]

if itens:
    for p in itens:
        with st.expander(f"Recuperar {p['nome']}"):
            nova_q = st.number_input("Nova Qtd", min_value=1, key=f"q_{p['id']}")
            if st.button("Confirmar", key=f"b_{p['id']}"):
                update_produto(p['id'], p['nome'], p['preco'], nova_q, p['marca'], p['estilo'], p['tipo'], p['foto'], p['data_validade'])
                st.rerun()
else:
    st.success("Tudo em dia!")
