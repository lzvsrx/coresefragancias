
import streamlit as st
import os
from datetime import datetime

# Protege importações com fallback completo
try:
    from utils.database import get_all_produtos, ASSETS_DIR
except ImportError as e:
    st.error(f"❌ Erro ao importar database: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Erro crítico no database: {e}")
    st.stop()

# --- FUNÇÕES AUXILIARES SEGURAS ---
def format_to_brl(value):
    """Formata float para BRL com tratamento robusto."""
    try:
        num = float(value)
        if num <= 0:
            return "R$ 0,00"
        formatted = f"{num:_.2f}"
        formatted = formatted.replace('.', 'X').replace('_', '.').replace('X', ',')
        return f"R$ {formatted}"
    except (ValueError, TypeError, AttributeError):
        return "R$ N/A"

def load_css(file_name="style.css"):
    """Carrega CSS silenciosamente."""
    try:
        if os.path.exists(file_name):
            with open(file_name, encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception:
        pass  # Silencioso

def format_date(date_str):
    """Formata data ISO para BR com fallback."""
    if not date_str or date_str in ['N/A', '-', 'None']:
        return 'N/A'
    try:
        return datetime.fromisoformat(date_str).strftime('%d/%m/%Y')
    except:
        return str(date_str)[:10]

def safe_int(value, default=0):
    try: return int(value)
    except: return default

def safe_float(value, default=0.0):
    try: return float(value)
    except: return default

# Configuração da página (CORRIGIDO - NO INÍCIO!)
st.set_page_config(
    page_title="Produtos Vendidos - Cores e Fragrâncias",
    page_icon="💰",
    layout="wide"
)

# Carrega CSS
load_css("style.css")

st.title("💰 Histórico de Itens Esgotados")
st.markdown("---")
st.info("📋 Produtos com **quantidade = 0** (esgotados por vendas ou exclusão)")

# --- CARGA DE DADOS COM FALLBACK ---
try:
    # Tenta parâmetro correto do database.py corrigido
    todos_produtos = get_all_produtos(include_sold=True)
except TypeError:
    # Fallback para versões antigas
    try:
        todos_produtos = get_all_produtos(True)
    except:
        todos_produtos = get_all_produtos()
except Exception as e:
    st.error(f"❌ Erro ao carregar produtos: {e}")
    todos_produtos = []

if not todos_produtos:
    st.warning("📦 **Nenhum produto encontrado** no sistema.")
    st.stop()

# Filtra produtos ESGOTADOS (quantidade == 0)
produtos_esgotados = [
    p for p in todos_produtos 
    if safe_int(p.get('quantidade', 0)) == 0 and p.get('nome')
]

if not produtos_esgotados:
    col1, col2 = st.columns(2)
    with col1:
        st.success("🎉 **BOM TRABALHO!**")
        st.info("✅ Todos os produtos têm estoque disponível.")
    with col2:
        st.metric("📊 Itens em Estoque", len(todos_produtos))
    st.stop()

# --- MÉTRICAS DE RESUMO ---
total_acumulado = 0.0
total_itens = len(produtos_esgotados)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📦 Itens Esgotados", total_itens)
with col2:
    st.metric("💰 Valor Total", format_to_brl(total_acumulado))
with col3:
    st.metric("📈 % do Estoque", f"{(total_itens/len(todos_produtos)*100):.1f}%" if todos_produtos else "0%")

st.markdown("---")

# --- LISTA DE PRODUTOS ESGOTADOS ---
for idx, produto in enumerate(produtos_esgotados):
    try:
        nome = produto.get('nome', 'N/A')[:50]
        preco = safe_float(produto.get('preco', 0))
        marca = produto.get('marca', 'N/A')
        tipo = produto.get('tipo', 'N/A')
        validade = produto.get('data_validade', 'N/A')
        foto = produto.get('foto')
        pid = produto.get('id', 'N/A')
        
        total_acumulado += preco
        
        with st.container(border=True):
            col_info, col_img, col_id = st.columns([3, 1, 1])
            
            with col_info:
                st.markdown(f"**✨ {nome}**")
                st.caption(f"**{marca}** • {tipo}")
                st.write(f"💰 **{format_to_brl(preco)}** por unidade")
                st.caption(f"📅 Validade: {format_date(validade)}")
            
            with col_img:
                if foto:
                    foto_path = os.path.join(ASSETS_DIR, foto) if ASSETS_DIR else foto
                    if os.path.exists(foto_path):
                        st.image(foto_path, width=120, use_column_width=True)
                    else:
                        st.markdown("🖼️")
                else:
                    st.markdown("🖼️")
            
            with col_id:
                st.caption(f"**ID:** {pid}")
                st.caption("**Qtd:** 0")
            
    except Exception as e:
        st.error(f"❌ Erro no item {idx}: {e}")
        continue

# --- RESUMO FINAL ---
st.markdown("---")
col_total1, col_total2 = st.columns(2)
with col_total1:
    st.success(f"💎 **Valor Total Esgotado:** {format_to_brl(total_acumulado)}")
with col_total2:
    st.info(f"📊 **{total_itens} itens** | **{len(todos_produtos)} total** no sistema")

st.caption(f"*Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}*")

