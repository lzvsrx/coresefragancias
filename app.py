import streamlit as st
import os
from utils.database import create_tables, get_all_produtos
from datetime import datetime

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(
    page_title="Cores e Fragrâncias by Berenice",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializa as tabelas do DB (garante que existem)
create_tables()

# Inicialização do estado de sessão
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = ""
if "role" not in st.session_state: st.session_state["role"] = "guest"

# Função para carregar CSS
def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
load_css()

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    if st.session_state["logged_in"]:
        st.success(f"👤 **{st.session_state['username']}**\n\nNível: `{st.session_state['role'].upper()}`")
        if st.button("Sair do Sistema"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["role"] = "guest"
            st.rerun()
    else:
        st.warning("🔒 Usuário não identificado")
        st.info("Acesse a **Área Administrativa** para entrar.")

# --- CONTEÚDO PRINCIPAL ---
st.title("🌸 Cores e Fragrâncias by Berenice")
st.markdown("---")

# --- DASHBOARD RÁPIDO (Apenas para usuários logados) ---
if st.session_state["logged_in"]:
    st.subheader("📊 Resumo do Estoque")
    
    # Busca dados para o dashboard
    produtos = get_all_produtos(include_out_of_stock=True)
    total_pecas = sum(p['quantidade'] for p in produtos)
    valor_total = sum(p['preco'] * p['quantidade'] for p in produtos)
    # Alerta para produtos com 3 ou menos unidades
    estoque_baixo = [p for p in produtos if 0 < p['quantidade'] <= 3]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Itens", f"{total_pecas} un")
    with col2:
        # Formatação para Real Brasileiro
        valor_brl = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.metric("Capital em Estoque", valor_brl)
    with col3:
        st.metric("Reposição Necessária", f"{len(estoque_baixo)} itens")

    if estoque_baixo:
        with st.expander("⚠️ Ver itens com estoque baixo"):
            for item in estoque_baixo:
                st.write(f"- {item['nome']} ({item['marca']}): **{item['quantidade']} unidades**")
    st.markdown("---")

# --- TEXTO INFORMATIVO ---
col_info, col_logo = st.columns([2, 1])

with col_info:
    st.markdown("""
    ### 🧭 Guia de Navegação
    Use o menu lateral para gerenciar a loja:
    
    * **Área Administrativa:** Clique aqui para fazer **Login** ou gerenciar usuários.
    * **Gerenciar Produtos:** Espaço para cadastrar novos itens, editar preços, excluir ou registrar vendas.
    * **Estoque Completo:** Visualização em lista de todos os itens disponíveis.
    * **Produtos Vendidos:** Histórico de itens que já foram esgotados.
    
    *Dica: Mantenha as fotos dos produtos sempre atualizadas para facilitar a identificação.*
    """)

with col_logo:
    try:
        if os.path.exists("assets/logo.png"):
            st.image("assets/logo.png", use_container_width=True)
        else:
            # Placeholder caso não haja logo
            st.markdown("<h1 style='text-align: center; font-size: 80px;'>🛍️</h1>", unsafe_allow_html=True)
    except Exception:
        pass

st.markdown("---")
st.caption(f"© {datetime.now().year} Cores e Fragrâncias - Sistema de Gestão Interna.")
