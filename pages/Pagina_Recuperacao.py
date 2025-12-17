import streamlit as st
from utils.database import get_all_produtos, update_produto
import os

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

st.title("🔄 Recuperação de Produtos")
st.markdown("Aqui estão os itens com estoque zero. Altere a quantidade para que voltem ao estoque.")

# Traz itens zerados diretamente do banco de dados
itens_zerados = [p for p in get_all_produtos(include_sold=True) if p['quantidade'] <= 0]

if not itens_zerados:
    st.success("Não há produtos zerados no banco de dados.")
else:
    for p in itens_zerados:
        with st.expander(f"Repor: {p['nome']}"):
            nova_qtd = st.number_input("Quantidade para Repor", min_value=1, value=5, key=f"q_{p['id']}")
            if st.button("Confirmar e Salvar", key=f"btn_{p['id']}"):
                update_produto(p['id'], p['nome'], p['preco'], nova_qtd, p['marca'], p['estilo'], p['tipo'], p['foto'], p['data_validade'])
                st.success("Produto recuperado!")
                st.rerun()
