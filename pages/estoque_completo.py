import streamlit as st
from utils.database import get_all_produtos, ASSETS_DIR
import os

def format_to_brl(value):
    try:
        return f"R$ {float(value):_.2f}".replace('.', ',').replace('_', '.')
    except: return "R$ N/A"

st.title("📦 Estoque Completo")

# CHAMADA: include_sold=True para garantir que nada suma
produtos = get_all_produtos(include_sold=True)

if not produtos:
    st.info("Nenhum produto cadastrado.")
else:
    # Filtros baseados na sua estrutura
    marcas = sorted(list({p.get("marca") for p in produtos if p.get("marca")}))
    marca_filtro = st.selectbox("Filtrar por Marca", ["Todas"] + marcas)

    produtos_filtrados = produtos
    if marca_filtro != "Todas":
        produtos_filtrados = [p for p in produtos if p.get("marca") == marca_filtro]

    for p in produtos_filtrados:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                if p.get("foto") and os.path.exists(os.path.join(ASSETS_DIR, p.get("foto"))):
                    st.image(os.path.join(ASSETS_DIR, p.get("foto")), width=120)
                else: st.write("📷 S/ Foto")
            
            with col2:
                st.subheader(p.get("nome"))
                qtd = p.get("quantidade", 0)
                status = "✅ Em Estoque" if qtd > 0 else "❌ Esgotado / Vendido"
                st.write(f"**{status}** | Quantidade: {qtd}")
                st.write(f"**Preço:** {format_to_brl(p.get('preco'))}")
        st.divider()
