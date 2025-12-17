import streamlit as st
from utils.database import get_all_produtos, ASSETS_DIR  # ✅ ASSETS_DIR agora exportado
from datetime import datetime
import os

def format_to_brl(value):
    """Formata um float para string no formato R$ 1.234.567,89."""
    try:
        num = float(value)
        formatted = f"{num:_.2f}"
        formatted = formatted.replace('.', 'X').replace('_', '.').replace('X', ',')
        return f"R$ {formatted}"
    except (ValueError, TypeError):
        return "R$ N/A"

def load_css(filename="style.css"):
    """Carrega e aplica o CSS personalizado."""
    if os.path.exists(filename):
        try:
            with open(filename, encoding='utf-8') as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar CSS: {e}")

# Configuração da página
st.set_page_config(page_title="Estoque - Cores e Fragrâncias")
load_css("style.css")  # Aplica o CSS

st.title("📦 Estoque Completo")

# Carga inicial dos dados
produtos = get_all_produtos(include_sold=True)

if not produtos:
    st.info("Nenhum produto cadastrado no estoque.")
else:
    # Coleta categorias únicas para filtros
    marcas = sorted(list(set(p.get('marca') for p in produtos if p.get('marca'))))
    estilos = sorted(list(set(p.get('estilo') for p in produtos if p.get('estilo'))))
    tipos = sorted(list(set(p.get('tipo') for p in produtos if p.get('tipo'))))
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        marca_filtro = st.selectbox("Filtrar por Marca", ["Todas"] + marcas)
    with col2:
        estilo_filtro = st.selectbox("Filtrar por Estilo", ["Todos"] + estilos)
    with col3:
        tipo_filtro = st.selectbox("Filtrar por Tipo", ["Todos"] + tipos)
    
    # Aplica filtros
    produtos_filtrados = produtos
    if marca_filtro != "Todas":
        produtos_filtrados = [p for p in produtos_filtrados if p.get('marca') == marca_filtro]
    if estilo_filtro != "Todos":
        produtos_filtrados = [p for p in produtos_filtrados if p.get('estilo') == estilo_filtro]
    if tipo_filtro != "Todos":
        produtos_filtrados = [p for p in produtos_filtrados if p.get('tipo') == tipo_filtro]
    
    st.markdown("---")
    st.subheader(f"📊 {len(produtos_filtrados)} produtos encontrados")
    
    # Cálculo total do estoque filtrado
    total_estoque = 0.0
    for p in produtos_filtrados:
        try:
            preco_float = float(p.get('preco', 0))
            quantidade_int = int(p.get('quantidade', 0))
            valor_produto = preco_float * quantidade_int
            total_estoque += valor_produto
        except (ValueError, TypeError):
            pass
    
    # Exibição dos produtos filtrados
    for p in produtos_filtrados:
        try:
            preco_float = float(p.get('preco', 0))
            quantidade_int = int(p.get('quantidade', 0))
            valor_produto = preco_float * quantidade_int
        except (ValueError, TypeError):
            preco_float, quantidade_int, valor_produto = 0, 0, 0
        
        st.markdown(f"**{p.get('nome', 'N/A')}**")
        st.write(f"**Marca:** {p.get('marca', 'N/A')} | **Estilo:** {p.get('estilo', 'N/A')} | **Tipo:** {p.get('tipo', 'N/A')}")
        st.write(f"**Preço Unitário:** {format_to_brl(preco_float)} | **Quantidade em Estoque:** {quantidade_int}")
        st.write(f"**Valor Total deste Item:** {format_to_brl(valor_produto)}")
        st.write(f"**Validade:** {p.get('data_validade', 'N/A')}")
        
        # Foto do produto
        if p.get('foto'):
            photo_path = os.path.join(ASSETS_DIR, p['foto'])
            if os.path.exists(photo_path):
                try:
                    st.image(photo_path, width=180, caption=p.get('nome'))
                except Exception:
                    st.info("❌ Erro ao carregar imagem.")
            else:
                st.info("📷 Sem foto ou caminho inválido.")
        else:
            st.info("📷 Sem foto.")
        
        st.markdown("---")
    
    # Total geral
    st.success(f"💰 **Valor Total em Estoque (filtrado):** {format_to_brl(total_estoque)}")[file:3]
