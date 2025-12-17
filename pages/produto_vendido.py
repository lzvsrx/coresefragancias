import streamlit as st
from utils.database import get_all_produtos
import os

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

def format_to_brl(value):
    try:
        num = float(value)
        return "R$ " + f"{num:_.2f}".replace('.', ',').replace('_', '.')
    except: return "R$ 0,00"

st.title("💰 Produtos Vendidos")
st.info("Abaixo estão os itens que saíram totalmente do estoque.")

# Filtra itens com quantidade 0 que foram marcados como vendidos
vendidos = [p for p in get_all_produtos(include_sold=True) if p['quantidade'] <= 0 and p['vendido'] == 1]

if not vendidos:
    st.info("Nenhuma venda total registrada.")
else:
    total_vendido_financeiro = 0.0
    
    for p in vendidos:
        valor_venda = float(p['preco'])
        total_vendido_financeiro += valor_venda
        
        with st.container():
            st.write(f"### {p['nome']}")
            st.write(f"**Marca:** {p['marca']} | **Valor da Venda:** {format_to_brl(valor_venda)}")
            st.write(f"**Data da Saída:** {p['data_ultima_venda'] or 'Não informada'}")
        st.divider()

    st.success(f"📊 **VALOR TOTAL DE VENDAS (ITENS ESGOTADOS): {format_to_brl(total_vendido_financeiro)}**")
