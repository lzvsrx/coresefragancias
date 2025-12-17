import streamlit as st
import os
from utils.database import get_all_produtos, ASSETS_DIR

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(page_title="Estoque - Cores e Fragrâncias", layout="wide")
load_css()

def format_brl(val):
    return f"R$ {float(val):_.2f}".replace('.', ',').replace('_', '.')

st.title("📦 Estoque Completo")

produtos = get_all_produtos(include_sold=True)
total_geral = 0.0

if not produtos:
    st.info("Estoque vazio.")
else:
    # Filtros
    marcas = sorted(list({p.get("marca") for p in produtos if p.get("marca")}))
    f_marca = st.sidebar.selectbox("Filtrar Marca", ["Todas"] + marcas)
    
    filtrados = [p for p in produtos if (f_marca == "Todas" or p['marca'] == f_marca)]

    for p in filtrados:
        sub = p['quantidade'] * p['preco']
        total_geral += sub
        with st.container():
            c1, c2 = st.columns([1, 4])
            with c1:
                img = os.path.join(ASSETS_DIR, p['foto']) if p['foto'] else ""
                if img and os.path.exists(img): st.image(img, width=120)
            with c2:
                st.subheader(p['nome'])
                st.write(f"**Qtd:** {p['quantidade']} | **Preço:** {format_brl(p['preco'])} | **Total:** {format_brl(sub)}")
                if p['quantidade'] <= 0: st.error("Esgotado")
        st.divider()

st.sidebar.metric("Valor Total em Estoque", format_brl(total_geral))
