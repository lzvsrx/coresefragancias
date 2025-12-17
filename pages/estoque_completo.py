import streamlit as st
from utils.database import get_all_produtos, ASSETS_DIR
import os

# --- Configuração de Página e CSS ---
st.set_page_config(page_title="Estoque - Cores e Fragrâncias", layout="wide")

st.markdown("""
<style>
    .product-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

def format_to_brl(value):
    try:
        num = float(value)
        return "R$ " + f"{num:_.2f}".replace('.', ',').replace('_', '.')
    except: return "R$ 0,00"

st.title("📦 Estoque Completo")

# include_sold=True para garantir que nada suma da lista mestre
produtos = get_all_produtos(include_sold=True)

if not produtos:
    st.info("O banco de dados está vazio.")
else:
    # Filtros
    c1, c2, c3 = st.columns(3)
    marcas = sorted(list({p.get("marca") for p in produtos if p.get("marca")}))
    estilos = sorted(list({p.get("estilo") for p in produtos if p.get("estilo")}))
    
    with c1: f_marca = st.selectbox("Marca", ["Todas"] + marcas)
    with c2: f_estilo = st.selectbox("Estilo", ["Todos"] + estilos)
    
    filtrados = [p for p in produtos if 
                 (f_marca == "Todas" or p['marca'] == f_marca) and 
                 (f_estilo == "Todos" or p['estilo'] == f_estilo)]

    st.subheader(f"Total: {len(filtrados)} itens")
    
    total_financeiro = 0.0
    for p in filtrados:
        qtd = p['quantidade']
        total_item = qtd * p['preco']
        total_financeiro += total_item
        
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                img_path = os.path.join(ASSETS_DIR, p['foto']) if p['foto'] else ""
                if img_path and os.path.exists(img_path): st.image(img_path, width=130)
                else: st.info("Sem foto")
            
            with col2:
                st.markdown(f"### {p['nome']}")
                st.write(f"**Marca:** {p['marca']} | **Tipo:** {p['tipo']}")
                st.write(f"**Preço Unit:** {format_to_brl(p['preco'])}")
                if qtd <= 0:
                    st.markdown("<span style='color:red; font-weight:bold;'>⚠️ ESGOTADO</span>", unsafe_allow_html=True)
                else:
                    st.write(f"**Estoque:** {qtd} unidades")
            
            with col3:
                st.metric("Subtotal", format_to_brl(total_item))
        st.divider()

    st.sidebar.success(f"Valor Total Filtrado:\n\n{format_to_brl(total_financeiro)}")
