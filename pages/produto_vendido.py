import streamlit as st
from utils.database import get_all_produtos
from datetime import datetime

st.title("💰 Relatório de Itens Vendidos (Esgotados)")

# Filtra itens que foram marcados como vendidos e estão com zero estoque
vendidos = [p for p in get_all_produtos(include_sold=True) if p['quantidade'] <= 0 and p['vendido'] == 1]

if not vendidos:
    st.info("Nenhum item totalmente vendido até o momento.")
else:
    total_vendas = sum(p['preco'] for p in vendidos)
    st.metric("Total em Vendas de Itens Esgotados", f"R$ {total_vendas:,.2f}")
    
    for p in vendidos:
        st.write(f"**Produto:** {p['nome']} | **Marca:** {p['marca']}")
        st.write(f"**Data da Venda:** {p['data_ultima_venda'] or 'N/A'}")
        st.divider()
