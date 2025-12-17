import streamlit as st
from utils.database import get_all_produtos, ASSETS_DIR
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

st.title("📦 Estoque Completo")

produtos = get_all_produtos(include_sold=True)

if not produtos:
    st.info("Nenhum produto cadastrado.")
else:
    # Filtros
    marcas = sorted(list({p.get("marca") for p in produtos if p.get("marca")}))
    f_marca = st.selectbox("Filtrar por Marca", ["Todas"] + marcas)
    
    filtrados = [p for p in produtos if (f_marca == "Todas" or p['marca'] == f_marca)]

    total_estoque_financeiro = 0.0

    for p in filtrados:
        qtd = int(p['quantidade'])
        preco = float(p['preco'])
        subtotal = qtd * preco
        total_estoque_financeiro += subtotal
        
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                path = os.path.join(ASSETS_DIR, p['foto']) if p['foto'] else ""
                if path and os.path.exists(path): st.image(path, width=100)
            with col2:
                st.subheader(p['nome'])
                st.write(f"**Marca:** {p['marca']} | **Qtd:** {qtd}")
                st.write(f"**Preço Unit.:** {format_to_brl(preco)}")
            with col3:
                st.metric("Subtotal", format_to_brl(subtotal))
        st.divider()

    st.success(f"💰 **VALOR TOTAL EM ESTOQUE (FILTRADO): {format_to_brl(total_estoque_financeiro)}**")
