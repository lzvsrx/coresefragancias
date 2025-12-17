import streamlit as st
from utils.database import get_all_produtos, ASSETS_DIR
import os
from datetime import datetime

st.title("💰 Histórico de Vendas")

# Filtra apenas o que tem quantidade 0 e foi marcado como vendido
todos = get_all_produtos(include_sold=True)
vendidos = [p for p in todos if p['quantidade'] <= 0 and p['vendido'] == 1]

if not vendidos:
    st.info("Nenhum item totalmente vendido no momento.")
else:
    for p in vendidos:
        with st.expander(f"{p['nome']} - Vendido em: {p['data_ultima_venda'][:10]}"):
            st.write(f"**Preço na venda:** R$ {p['preco']}")
            st.write(f"**Marca:** {p['marca']}")
            if st.button(f"Repor Estoque de {p['nome']}", key=p['id']):
                # Exemplo de como fazer o produto "voltar" ao estoque ativo
                from utils.database import update_produto
                update_produto(p['id'], p['nome'], p['preco'], 10, p['marca'], p['estilo'], p['tipo'], p['foto'], p['data_validade'])
                st.rerun()
