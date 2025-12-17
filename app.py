
import streamlit as st
import os
from datetime import datetime

# Protege import em caso de problema no módulo de banco de dados
try:
    from utils.database import create_tables, get_all_produtos
except Exception as e:
    st.set_page_config(
        page_title="Cores e Fragrâncias by Berenice",
        page_icon="🌸",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.error(f"Erro ao importar módulo de banco de dados: {e}")
    st.stop()

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(
    page_title="Cores e Fragrâncias by Berenice",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializa as tabelas do DB (garante que existem)
try:
    create_tables()
except Exception as e:
    st.error(f"Erro ao inicializar o banco de dados: {e}")
    st.stop()

# Inicialização do estado de sessão
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = "guest"

# Função para carregar CSS
def load_css(file_name="style.css"):
    try:
        if os.path.exists(file_name):
            with open(file_name, encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        # Não quebra a aplicação se o CSS falhar
        st.warning(f"Não foi possível carregar o CSS ({file_name}): {e}")

load_css()

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    if st.session_state["logged_in"]:
        username = st.session_state.get("username", "")
        role = st.session_state.get("role", "guest")
        st.success(
            f"👤 **{username or 'Usuário'}**\n\nNível: `{str(role).upper()}`"
        )
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
if st.session_state.get("logged_in", False):
    st.subheader("📊 Resumo do Estoque")

    # Busca dados para o dashboard com tratamento de erro
    try:
        # garante compatibilidade com seu database.py (usa include_sold=True)
        produtos = get_all_produtos(include_sold=True)
    except TypeError:
        # fallback se a função não aceitar parâmetros nomeados
        try:
            produtos = get_all_produtos()
        except Exception as e:
            st.error(f"Erro ao carregar produtos: {e}")
            produtos = []
    except Exception as e:
        st.error(f"Erro ao carregar produtos: {e}")
        produtos = []

    if not produtos:
        st.info("Nenhum produto encontrado para o resumo de estoque.")
    else:
        # Segurança de tipos / chaves
        total_pecas = 0
        valor_total = 0.0
        estoque_baixo = []

        for p in produtos:
            try:
                qtd = int(p.get("quantidade", 0))
                preco = float(p.get("preco", 0))

                total_pecas += max(qtd, 0)
                valor_total += max(qtd, 0) * max(preco, 0.0)

                if 0 < qtd <= 3:
                    estoque_baixo.append(p)
            except (TypeError, ValueError, AttributeError):
                # Ignora registros malformados sem quebrar o app
                continue

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de Itens", f"{total_pecas} un")

        with col2:
            # Formatação segura para Real Brasileiro
            try:
                valor_brl = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except Exception:
                valor_brl = "R$ 0,00"
            st.metric("Capital em Estoque", valor_brl)

        with col3:
            st.metric("Reposição Necessária", f"{len(estoque_baixo)} itens")

        if estoque_baixo:
            with st.expander("⚠️ Ver itens com estoque baixo"):
                for item in estoque_baixo:
                    nome = item.get("nome", "Sem nome")
                    marca = item.get("marca", "Sem marca")
                    try:
                        qtd_item = int(item.get("quantidade", 0))
                    except (TypeError, ValueError):
                        qtd_item = 0
                    st.write(f"- {nome} ({marca}): **{qtd_item} unidades**")
        st.markdown("---")

# --- TEXTO INFORMATIVO ---
col_info, col_logo = st.columns([2, 1])

with col_info:
    st.markdown(
        """
    ### 🧭 Guia de Navegação
    Use o menu lateral para gerenciar a loja:
    
    * **Área Administrativa:** Clique aqui para fazer **Login** ou gerenciar usuários.
    * **Gerenciar Produtos:** Espaço para cadastrar novos itens, editar preços, excluir ou registrar vendas.
    * **Estoque Completo:** Visualização em lista de todos os itens disponíveis.
    * **Produtos Vendidos:** Histórico de itens que já foram esgotados.
    
    *Dica: Mantenha as fotos dos produtos sempre atualizadas para facilitar a identificação.*
    """
    )

with col_logo:
    try:
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            # Placeholder caso não haja logo
            st.markdown(
                "<h1 style='text-align: center; font-size: 80px;'>🛍️</h1>",
                unsafe_allow_html=True,
            )
    except Exception:
        # Não quebra se der erro ao carregar a imagem
        st.markdown(
            "<h1 style='text-align: center; font-size: 80px;'>🛍️</h1>",
            unsafe_allow_html=True,
        )

st.markdown("---")
st.caption(
    f"© {datetime.now().year} Cores e Fragrâncias - Sistema de Gestão Interna."
)
