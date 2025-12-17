import streamlit as st
import os
from utils.database import get_all_produtos, update_produto

st.set_page_config(page_title="Recuperação")
if os.path.exists("style.css"):
    with open("style.css", encoding='utf-8') as f: st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("🔄 Recuperação de Itens")
st.info("Itens zerados no banco aparecem aqui para você repor estoque.")

itens = [p for p in get_all_produtos(include_sold=True) if p['quantidade'] <= 0]

for p in itens:
    with st.expander(f"Repor {p['nome']}"):
        nova_qtd = st.number_input("Qtd", min_value=1, key=f"rec_{p['id']}")
        if st.button("Salvar", key=f"btn_{p['id']}"):
            update_produto(p['id'], p['nome'], p['preco'], nova_qtd, p['marca'], p['estilo'], p['tipo'], p['foto'], p['data_validade'])
            st.rerun()
