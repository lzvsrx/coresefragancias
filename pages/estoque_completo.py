
import streamlit as st
from datetime import datetime
import os

# Protege import com fallback completo
try:
    from utils.database import (
        get_all_produtos, ASSETS_DIR, MARCAS, ESTILOS, TIPOS
    )
except ImportError as e:
    st.error(f"❌ Erro ao importar database: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Erro crítico no database: {e}")
    st.stop()

def format_to_brl(value):
    """Formata um float para string no formato R$ 1.234.567,89."""
    try:
        num = float(value)
        if num <= 0:
            return "R$ 0,00"
        formatted = f"{num:_.2f}"
        formatted = formatted.replace('.', 'X').replace('_', '.').replace('X', ',')
        return f"R$ {formatted}"
    except (ValueError, TypeError, AttributeError):
        return "R$ N/A"

def load_css(filename="style.css"):
    """Carrega CSS silenciosamente (não quebra se falhar)."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass  # Silencioso

def format_date(date_str):
    """Formata data ISO para formato brasileiro com fallback."""
    if not date_str or date_str == 'N/A' or date_str == '-':
        return 'N/A'
    try:
        return datetime.fromisoformat(date_str).strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        return str(date_str)[:10]  # Primeiros 10 chars como fallback

def safe_get(value, default='N/A'):
    """Acesso seguro a dicionários."""
    return value.get('value', default) if hasattr(value, 'get') else str(value)[:50]

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

# Carga inicial dos dados COM TRATAMENTO
@st.cache_data(ttl=300)
def load_produtos():
    """Carrega produtos com fallback."""
    try:
        return get_all_produtos(include_sold=True)
    except TypeError:
        # Fallback se parâmetro nomeado não existir
        try:
            return get_all_produtos(True)
        except:
            return get_all_produtos()
    except Exception as e:
        st.error(f"Erro ao carregar produtos: {e}")
        return []

produtos = load_produtos()

if not produtos:
    st.info("👆 **Nenhum produto cadastrado no estoque.**")
    st.info("💡 Use a página **Gerenciar Produtos** para adicionar itens.")
    st.stop()

# Coleta categorias únicas (segura)
def get_unique_categories(field):
    """Coleta categorias únicas com tratamento."""
    try:
        return sorted(list(set(p.get(field, '') for p in produtos if p.get(field))))
    except Exception:
        return []

marcas = get_unique_categories('marca') or [m for m in MARCAS[:10] if m]
estilos = get_unique_categories('estilo') or [e for e in ESTILOS[:10] if e]
tipos = get_unique_categories('tipo') or [t for t in TIPOS[:10] if t]

# Filtros em colunas
col1, col2, col3 = st.columns(3)
with col1:
    marca_filtro = st.selectbox("🔍 Filtrar por Marca", ["Todas"] + marcas, key="marca_filtro")
with col2:
    estilo_filtro = st.selectbox("🔍 Filtrar por Estilo", ["Todos"] + estilos, key="estilo_filtro")
with col3:
    tipo_filtro = st.selectbox("🔍 Filtrar por Tipo", ["Todos"] + tipos, key="tipo_filtro")

# Filtros adicionais
col4, col5, col6 = st.columns(3)
with col4:
    qtd_min = st.number_input("Mín. Qtd.", min_value=0, value=0, step=1, key="qtd_min")
with col5:
    busca_nome = st.text_input("🔍 Buscar nome", key="busca_nome")
with col6:
    mostrar_sem_estoque = st.checkbox("Incluir sem estoque", key="sem_estoque")

st.markdown("---")

# APLICA FILTROS (ROBUSTO)
produtos_filtrados = produtos[:]

if marca_filtro != "Todas":
    produtos_filtrados = [p for p in produtos_filtrados if safe_get(p, '').lower() == marca_filtro.lower()]
if estilo_filtro != "Todos":
    produtos_filtrados = [p for p in produtos_filtrados if safe_get(p, 'estilo').lower() == estilo_filtro.lower()]
if tipo_filtro != "Todos":
    produtos_filtrados = [p for p in produtos_filtrados if safe_get(p, 'tipo').lower() == tipo_filtro.lower()]
if qtd_min > 0:
    produtos_filtrados = [p for p in produtos_filtrados if safe_int(p.get('quantidade', 0)) >= qtd_min]
if busca_nome:
    produtos_filtrados = [p for p in produtos_filtrados if busca_nome.lower() in safe_get(p, 'nome').lower()]
if not mostrar_sem_estoque:
    produtos_filtrados = [p for p in produtos_filtrados if safe_int(p.get('quantidade', 0)) > 0]

# ESTATÍSTICAS
if produtos_filtrados:
    total_filtrados = len(produtos_filtrados)
    em_estoque = len([p for p in produtos_filtrados if safe_int(p.get('quantidade', 0)) > 0])
    total_valor = 0.0
    
    for p in produtos_filtrados:
        try:
            total_valor += float(p.get('preco', 0)) * int(p.get('quantidade', 0))
        except:
            pass

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Total Itens", total_filtrados)
    with col2:
        st.metric("✅ Em Estoque", em_estoque)
    with col3:
        st.metric("💰 Valor Total", format_to_brl(total_valor))
    with col4:
        st.metric("🔍 Filtrados", f"{len(produtos)} → {total_filtrados}")

st.markdown("---")
st.subheader(f"📋 {len(produtos_filtrados)} produtos encontrados")

if not produtos_filtrados:
    st.warning("😅 Nenhum produto corresponde aos filtros.")
    st.stop()

# LISTA DE PRODUTOS (ROBUSTA)
for idx, produto in enumerate(produtos_filtrados):
    with st.container(border=True):
        # Header
        col_nome, col_id = st.columns([3, 1])
        with col_nome:
            st.markdown(f"**{safe_get(produto, 'nome')}**")
        with col_id:
            st.caption(f"ID: {safe_get(produto, 'id')}")
        
        # Detalhes
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Marca:** {safe_get(produto, 'marca')}")
            st.write(f"**Estilo:** {safe_get(produto, 'estilo')}")
        with col2:
            st.write(f"**Tipo:** {safe_get(produto, 'tipo')}")
            st.write(f"**Validade:** {format_date(safe_get(produto, 'data_validade'))}")
        
        # Valores
        col_val1, col_val2 = st.columns(2)
        with col_val1:
            qtd = safe_int(produto.get('quantidade', 0))
            st.metric("Qtd", qtd)
        with col_val2:
            preco = safe_float(produto.get('preco', 0))
            valor_total = preco * qtd
            st.metric("Valor", format_to_brl(valor_total))
        
        # Foto segura
        foto = produto.get('foto')
        if foto:
            foto_path = os.path.join(ASSETS_DIR, foto) if 'ASSETS_DIR' in globals() else foto
            if os.path.exists(foto_path):
                col_img, col_status = st.columns([1, 3])
                with col_img:
                    st.image(foto_path, width=100, use_column_width=True)
                with col_status:
                    if qtd == 0:
                        st.error("❌ SEM ESTOQUE")
                    elif qtd <= 3:
                        st.warning(f"⚠️ Baixo: {qtd}un")
                    else:
                        st.success(f"✅ OK: {qtd}un")
            else:
                st.info("📷 Foto não encontrada")
        else:
            st.info("📷 Sem foto")
        
        st.markdown("─" * 50)

# FOOTER
st.markdown("---")
col1, col2 = st.columns([1, 2])
with col1:
    st.success(f"💰 **TOTAL FILTRADO:** {format_to_brl(total_valor)}")
with col2:
    st.caption(f"*Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | {len(produtos)} itens totais*")

def safe_float(value):
    try: return float(value)
    except: return 0.0

def safe_int(value):
    try: return int(value)
    except: return 0
