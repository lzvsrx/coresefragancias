import streamlit as st
from utils.database import get_all_produtos, ASSETS_DIR
import os

def format_to_brl(value):
    try:
        return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except: return "R$ 0,00"

st.set_page_config(page_title="Estoque Ativo")
st.title("📦 Estoque Disponível")

# Buscamos apenas produtos que possuem quantidade > 0 para não misturar com os vendidos
produtos = get_all_produtos(include_out_of_stock=False)

if not produtos:
    st.info("Não há produtos disponíveis no estoque no momento.")
else:
    # Filtros
    col1, col2, col3 = st.columns(3)
    marcas = sorted(list({p['marca'] for p in produtos if p['marca']}))
    with col1: m_filter = st.selectbox("Marca", ["Todas"] + marcas)
    
    # Aplica Filtro
    disp = [p for p in produtos if (m_filter == "Todas" or p['marca'] == m_filter)]
    
    total_valor = 0.0
    for p in disp:
        with st.container():
            col_img, col_txt = st.columns([1, 3])
            val_item = float(p['preco']) * int(p['quantidade'])
            total_valor += val_item
            
            with col_txt:
                st.subheader(p['nome'])
                st.write(f"**Qtd:** {p['quantidade']} | **Preço:** {format_to_brl(p['preco'])}")
                st.write(f"**Total Item:** {format_to_brl(val_item)}")
            
            if p['foto']:
                img_path = os.path.join(ASSETS_DIR, p['foto'])
                if os.path.exists(img_path): col_img.image(img_path, width=120)
            st.divider()

    st.success(f"💰 Valor Total em Estoque: {format_to_brl(total_valor)}")
