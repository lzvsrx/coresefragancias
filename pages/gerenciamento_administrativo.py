import streamlit as st
import os
import pandas as pd

# Protege import com fallback completo
try:
    from utils.database import add_user, get_user, get_all_users, hash_password
except ImportError as e:
    st.error(f"❌ Erro ao importar database: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Erro crítico no database: {e}")
    st.stop()

# --- Funções Auxiliares SEGURAS ---
def load_css(file_name="style.css"):
    """Carrega CSS silenciosamente."""
    try:
        if os.path.exists(file_name):
            with open(file_name, encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception:
        pass  # Silencioso - não quebra

def safe_session_get(key, default=None):
    """Acesso seguro ao session_state."""
    return st.session_state.get(key, default)

# Configuração da página (CORRIGIDO - ANTES de qualquer st.*)
st.set_page_config(
    page_title="Área Administrativa - Cores e Fragrâncias",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carrega CSS
load_css("style.css")

st.title("🔐 Área Administrativa")
st.markdown("---")

# Inicializa estados de sessão (SEGURO)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = "guest"

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    if safe_session_get("logged_in"):
        username = safe_session_get("username", "Usuário")
        role = safe_session_get("role", "guest")
        st.success(f"✅ **Conectado**\n\n👤 **{username}**\n\n🎯 **{role.upper()}**")
        
        if st.button("🚪 Sair do Sistema", type="primary"):
            # Limpa estados de forma segura
            keys_to_clear = ["logged_in", "username", "role", "chat_history", "chat_state"]
            for key in keys_to_clear:
                st.session_state.pop(key, None)
            st.success("Sessão encerrada com sucesso!")
            st.rerun()
    else:
        st.info("🔒 Faça login para continuar")

# --- LÓGICA PRINCIPAL ---
if not safe_session_get("logged_in"):
    # FORMULÁRIO DE LOGIN (ROBUSTO)
    st.info("👋 **Por favor, identifique-se** para acessar as funções administrativas.")
    
    with st.form("form_login", clear_on_submit=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            username = st.text_input("👤 Nome de usuário", placeholder="admin")
        with col2:
            password = st.text_input("🔑 Senha", type="password", placeholder="123")
        
        submit = st.form_submit_button("🚀 Entrar", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("❌ Preencha **usuário** e **senha**.")
            else:
                try:
                    user = get_user(username)
                    if user and user.get("password") == hash_password(password):
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username
                        st.session_state["role"] = user.get('role', 'guest')
                        st.success(f"🎉 Bem-vindo(a), **{username}**!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ **Usuário ou senha inválidos.**")
                        st.info("💡 Credenciais padrão: **admin** / **123**")
                except Exception as e:
                    st.error(f"❌ Erro no login: {str(e)[:50]}")

else:
    # INTERFACE ADMIN (USUÁRIO LOGADO)
    username = safe_session_get("username")
    role = safe_session_get("role")
    
    st.success(f"✅ **{username}** logado como **{role.upper()}**")
    st.markdown("---")
    
    # Opções horizontais
    col_options = st.columns(3)
    dashboard = col_options[0].button("📊 Dashboard", use_container_width=True)
    cadastrar = col_options[1].button("➕ Novo Usuário", use_container_width=True)
    lista = col_options[2].button("👥 Usuários", use_container_width=True)
    
    st.markdown("---")
    
    if dashboard:
        st.subheader("📊 Dashboard Administrativo")
        st.info(f"🔐 Você está logado com privilégios de: **{role.upper()}**")
        st.success("✅ **Acesso liberado** para todas as páginas do sistema!")
        st.markdown("""
        ### 📋 **Páginas Disponíveis:**
        - **Gerenciar Produtos** - CRUD completo
        - **Estoque Completo** - Visualização + filtros  
        - **Chatbot** - Comandos rápidos
        """)
    
    elif cadastrar:
        st.subheader("➕ Cadastrar Novo Usuário")
        
        # Verificação de permissão
        if role != 'admin':
            st.error("🚫 **Apenas ADMINISTRADORES** podem criar usuários.")
        else:
            with st.form("form_cadastro", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    new_user = st.text_input("👤 Novo usuário", max_chars=20)
                    new_role = st.selectbox("🎯 Nível", ["staff", "admin"])
                with col2:
                    new_pass = st.text_input("🔑 Senha", type="password", max_chars=50)
                    confirm_pass = st.text_input("🔒 Confirmar senha", type="password")
                
                submit_user = st.form_submit_button("💾 Criar Usuário", use_container_width=True)
                
                if submit_user:
                    # Validações completas
                    if not all([new_user, new_pass]):
                        st.error("❌ **Preencha todos os campos**.")
                    elif len(new_pass) < 3:
                        st.error("❌ Senha deve ter **no mínimo 3 caracteres**.")
                    elif new_pass != confirm_pass:
                        st.error("❌ **Senhas não coincidem**.")
                    else:
                        try:
                            existing_user = get_user(new_user)
                            if existing_user:
                                st.error("❌ **Usuário já existe**.")
                            else:
                                success = add_user(new_user, new_pass, new_role)
                                if success:
                                    st.success(f"🎉 **{new_user}** criado como **{new_role.upper()}**!")
                                    st.balloons()
                                else:
                                    st.error("❌ **Falha ao criar usuário** (nome duplicado?).")
                        except Exception as e:
                            st.error(f"❌ Erro: {str(e)[:50]}")
    
    elif lista or True:  # Default
        st.subheader("👥 Lista de Usuários")
        
        if role != 'admin':
            st.warning("👀 **Visualização básica** (apenas admins veem detalhes)")
            st.info(f"Você ({username}) tem nível **{role.upper()}**")
        else:
            try:
                users = get_all_users()
                if users:
                    # Tabela com Pandas (segura)
                    df_users = pd.DataFrame(users)
                    if not df_users.empty:
                        st.dataframe(
                            df_users[['username', 'role']], 
                            use_container_width=True,
                            hide_index=True
                        )
                        st.success(f"📊 **{len(users)} usuários** cadastrados")
                    else:
                        st.info("📭 Nenhum usuário encontrado.")
                else:
                    st.warning("⚠️ **Lista vazia** - Cadastre o primeiro usuário!")
            except Exception as e:
                st.error(f"❌ Erro ao listar usuários: {str(e)[:50]}")
                st.info("💡 Tente recarregar a página.")

# --- FOOTER ---
st.markdown("---")
st.caption(f"🔐 © {datetime.now().year} Cores e Fragrâncias - Área Administrativa")
