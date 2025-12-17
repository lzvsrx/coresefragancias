import streamlit as st
from utils.database import *

st.set_page_config(page_title="Vendidos", page_icon="💰")
load_css()
st.title("💰 Itens Esgotados")

produtos = get_all_produtos(include_sold=True)
esgotados = [p for p in produtos if safe_int(p.get('quantidade', 0)) == 0]

if not esgotados:
    st.success("🎉 Nenhum esgotado!")
else:
    total = sum(safe_float(p['preco']) for p in esgotados)
    st.metric("Itens", len(esgotados))
    st.metric("Valor", format_to_brl(total))
    
    for p in esgotados:
        st.write(f"**{p['nome']}** - R${p['preco']} ({p.get('marca')})")
