import streamlit as st
import os
from utils.database import create_tables, get_all_produtos
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Cores e Fragrâncias by Berenice",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializa as tabelas do DB
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
        st.warning("🔒 Você não está logado.")
        st.info("Acesse a **Área Administrativa** no menu ao lado para entrar.")

# --- CONTEÚDO PRINCIPAL ---
st.title("🌸 Cores e Fragrâncias by Berenice")
st.subheader("Sistema de Gestão de Estoque e Vendas")
st.markdown("---")

# --- DASHBOARD RÁPIDO (Apenas se logado) ---
if st.session_state["logged_in"]:
    st.markdown("### 📊 Resumo do Negócio")
    
    # Busca dados reais para o resumo
    produtos = get_all_produtos(include_sold=True)
    total_itens = sum(p['quantidade'] for p in produtos)
    total_valor = sum(p['preco'] * p['quantidade'] for p in produtos)
    itens_alerta = [p for p in produtos if 0 < p['quantidade'] <= 3]
    itens_esgotados = [p for p in produtos if p['quantidade'] == 0]

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total em Peças", f"{total_itens} un.")
    with col2:
        st.metric("Valor do Estoque", f"R$ {total_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with col3:
        st.metric("Alerta de Estoque (Baixo)", f"{len(itens_alerta)} itens", delta_color="inverse")
    with col4:
        st.metric("Esgotados", f"{len(itens_esgotados)} itens")

    if itens_alerta:
        with st.expander("⚠️ Ver itens com estoque baixo (3 ou menos)"):
            for item in itens_alerta:
                st.write(f"- {item['nome']} ({item['marca']}): **{item['quantidade']} unidades**")

st.markdown("---")

# --- INSTRUÇÕES E NAVEGAÇÃO ---
col_texto, col_logo = st.columns([2, 1])

with col_texto:
    st.markdown("""
    ### 🧭 Como navegar:
    
    1.  **Área Administrativa:** Clique aqui primeiro para fazer login ou criar contas.
    2.  **Gerenciar Produtos:** Onde a mágica acontece. Cadastre itens, edite preços e registre vendas.
    3.  **Chatbot Operacional:** Uma forma rápida de vender ou consultar o estoque apenas digitando.
    4.  **Estoque Completo:** Uma visão em tabela para conferência rápida.

    *Dica: Mantenha as datas de validade atualizadas para evitar perdas!*
    """)

with col_logo:
    try:
        if os.path.exists("assets/logo.png"):
            st.image("assets/logo.png", use_container_width=True)
        else:
            # Caso não tenha logo, mostramos um ícone decorativo
            st.markdown("<h1 style='text-align: center; font-size: 100px;'>🛍️</h1>", unsafe_allow_html=True)
    except Exception:
        pass

st.markdown("---")
st.caption(f"© {datetime.now().year} Cores e Fragrâncias - Gerenciamento Interno.")
