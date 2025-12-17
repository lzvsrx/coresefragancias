import streamlit as st
from datetime import datetime
import os
from utils.database import get_all_produtos

# Exemplo de uso correto agora:
todos = get_all_produtos(include_out_of_stock=True)
def format_to_brl(value):
    try: return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except: return "R$ 0,00"

st.title("💰 Histórico de Vendas / Esgotados")
vendidos = [p for p in todos if p.get('vendido') == 1]

if not vendidos:
    st.info("Nenhuma venda registrada ainda.")
else:
    total_vendas = 0.0
    for p in vendidos:
        # Se a quantidade for 0, ele aparece aqui como "Esgotado"
        # Se a quantidade for > 0, ele aparece aqui como "Item com vendas parciais"
        status = "🔴 ESGOTADO" if p['quantidade'] == 0 else "🟡 EM ESTOQUE (Venda Parcial)"
        
        with st.expander(f"{p['nome']} - {status}"):
            st.write(f"**Última Venda:** {p['data_ultima_venda']}")
            st.write(f"**Preço unitário na venda:** {format_to_brl(p['preco'])}")
            if p['foto']:
                path = os.path.join(ASSETS_DIR, p['foto'])
                if os.path.exists(path): st.image(path, width=100)

