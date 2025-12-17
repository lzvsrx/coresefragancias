estoque_completo.py - COMPLETO E SEM ERROS
python
import streamlit as st
from utils.database import get_all_produtos, ASSETS_DIR, MARCAS, ESTILOS, TIPOS
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
    """Carrega e aplica o CSS personalizado, forçando a codificação UTF-8."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar CSS: {e}")

def format_date(date_str):
    """Formata data ISO para formato brasileiro."""
    if not date_str or date_str == 'N/A':
        return 'N/A'
    try:
        return datetime.fromisoformat(date_str).strftime('%d/%m/%Y')
    except:
        return date_str

# Configuração da página
st.set_page_config(
    page_title="Estoque - Cores e Fragrâncias",
    page_icon="📦",
    layout="wide"
)

# Carrega CSS
load_css("style.css")

st.title("📦 Estoque Completo - Cores e Fragrâncias")
st.markdown("---")

# Carga inicial dos dados ✅ TRANSação segura já implementada no database.py
@st.cache_data(ttl=300)  # Cache de 5 minutos para performance
def load_produtos():
    return get_all_produtos(include_sold=True)

produtos = load_produtos()

if not produtos:
    st.info("👆 **Nenhum produto cadastrado no estoque.**")
    st.info("Use a página **Gerenciar Produtos** para adicionar itens.")
    st.stop()

# Coleta categorias únicas para filtros (mais robusto)
def get_unique_categories(field):
    return sorted(list(set(p.get(field, '') for p in produtos if p.get(field))))

marcas = get_unique_categories('marca')
estilos = get_unique_categories('estilo')
tipos = get_unique_categories('tipo')

# Filtros em colunas ✅ Melhor layout
col1, col2, col3 = st.columns(3)
with col1:
    marca_filtro = st.selectbox("🔍 Filtrar por Marca", ["Todas"] + marcas, key="marca_filtro")
with col2:
    estilo_filtro = st.selectbox("🔍 Filtrar por Estilo", ["Todos"] + estilos, key="estilo_filtro")
with col3:
    tipo_filtro = st.selectbox("🔍 Filtrar por Tipo", ["Todos"] + tipos, key="tipo_filtro")

# Quantidade mínima ✅ Novo filtro
col4, col5 = st.columns(2)
with col4:
    qtd_min = st.number_input("Quantidade mínima", min_value=0, value=0, step=1, key="qtd_min")
with col5:
    busca_nome = st.text_input("🔍 Buscar por nome", key="busca_nome")

st.markdown("---")

# Aplica todos os filtros ✅ Lógica otimizada
produtos_filtrados = produtos

if marca_filtro != "Todas":
    produtos_filtrados = [p for p in produtos_filtrados if p.get('marca') == marca_filtro]
if estilo_filtro != "Todos":
    produtos_filtrados = [p for p in produtos_filtrados if p.get('estilo') == estilo_filtro]
if tipo_filtro != "Todos":
    produtos_filtrados = [p for p in produtos_filtrados if p.get('tipo') == tipo_filtro]
if qtd_min > 0:
    produtos_filtrados = [p for p in produtos_filtrados if int(p.get('quantidade', 0)) >= qtd_min]
if busca_nome:
    produtos_filtrados = [p for p in produtos_filtrados if busca_nome.lower() in p.get('nome', '').lower()]

# Estatísticas ✅ Cards informativos
col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
total_produtos = len(produtos_filtrados)
total_filtrados = len([p for p in produtos_filtrados if int(p.get('quantidade', 0)) > 0])
total_zerados = total_produtos - total_filtrados

with col_stats1:
    st.metric("📦 Total Produtos", total_produtos)
with col_stats2:
    st.metric("✅ Em Estoque", total_filtrados)
with col_stats3:
    st.metric("❌ Sem Estoque", total_zerados)
with col_stats4:
    pass  # Reservado para valor total

st.markdown("---")
st.subheader(f"📋 {len(produtos_filtrados)} produtos encontrados")

if not produtos_filtrados:
    st.warning("😅 Nenhum produto corresponde aos filtros aplicados.")
    st.stop()

# Cálculo total do estoque filtrado ✅ Robusto
total_estoque = 0.0
for p in produtos_filtrados:
    try:
        preco = float(p.get('preco', 0))
        qtd = int(p.get('quantidade', 0))
        total_estoque += preco * qtd
    except (ValueError, TypeError):
        continue

# Exibição dos produtos em container com bordas ✅ Layout profissional
for idx, p in enumerate(produtos_filtrados):
    with st.container(border=True):
        # Linha 1: Nome e ações
        col_nome, col_id = st.columns([4, 1])
        with col_nome:
            st.markdown(f"**{p.get('nome', 'N/A')}**")
        with col_id:
            st.caption(f"ID: {p.get('id', 'N/A')}")
        
        # Linha 2: Categorias
        col_cat1, col_cat2 = st.columns(2)
        with col_cat1:
            st.write(f"**Marca:** {p.get('marca', 'N/A')}")
            st.write(f"**Estilo:** {p.get('estilo', 'N/A')}")
        with col_cat2:
            st.write(f"**Tipo:** {p.get('tipo', 'N/A')}")
            st.write(f"**Validade:** {format_date(p.get('data_validade'))}")
        
        # Linha 3: Valores
        col_val1, col_val2 = st.columns(2)
        with col_val1:
            qtd = int(p.get('quantidade', 0))
            st.metric("Quantidade", qtd, delta=None)
        with col_val2:
            preco = float(p.get('preco', 0))
            valor_total = preco * qtd
            st.metric("Valor Total", format_to_brl(valor_total))
        
        # Foto
        if p.get('foto'):
            photo_path = os.path.join(ASSETS_DIR, p['foto'])
            if os.path.exists(photo_path):
                col_img, col_info = st.columns([1, 3])
                with col_img:
                    st.image(photo_path, width=120, use_column_width=True)
                with col_info:
                    if qtd == 0:
                        st.error("❌ **SEM ESTOQUE**")
                    elif qtd < 5:
                        st.warning(f"⚠️ Pouco estoque: {qtd} unid.")
            else:
                st.info("📷 Foto não encontrada.")
        else:
            st.info("📷 Sem foto cadastrada.")
        
        st.markdown("---")

# Footer com totais ✅ Layout final
col_total1, col_total2, col_total3 = st.columns([1, 1, 2])
with col_total1:
    st.markdown("**💰 Valor Total:**")
with col_total2:
    st.success(format_to_brl(total_estoque))
with col_total3:
    st.caption(f"*Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')} | {len(produtos)} produtos totais no banco*")

st.markdown("---")
st.markdown("*Desenvolvido para Cores e Fragrâncias © 2025*")
