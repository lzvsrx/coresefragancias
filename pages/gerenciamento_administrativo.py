import streamlit as st
import os
from utils.database import add_user, get_user, get_all_users, hash_password

# --- Funções Auxiliares ---

def load_css(file_name="style.css"):
    """Carrega e aplica o CSS personalizado com codificação UTF-8."""
    if os.path.exists(file_name):
        try:
            with open(file_name, encoding='utf-8') as f: 
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar CSS: {e}")

# Configuração da página (deve vir antes de quase tudo)
# st.set_page_config(page_title="Área Administrativa - Cores e Fragrâncias")

load_css("style.css")

st.title("🔐 Área Administrativa")
st.markdown("---")

# Inicializa o estado de login se não existir
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- BARRA LATERAL (SIDEBAR) ---
if st.session_state.get("logged_in"):
    with st.sidebar:
        st.success(f"✅ Conectado\n\n**Usuário:** {st.session_state.get('username')}\n\n**Nível:** {st.session_state.get('role').upper()}")
        if st.button("Sair do Sistema"):
            # Limpa o estado da sessão de forma segura
            for key in ["logged_in", "username", "role", "chat_history", "chat_state"]:
                if key in st.session_state:
                    st.session_state.pop(key)
            st.success("Sessão encerrada.")
            st.rerun()

# --- LÓGICA DE INTERFACE ---

if not st.session_state.get("logged_in"):
    # Interface para usuários não logados: Apenas Login
    st.info("Por favor, identifique-se para acessar as funções administrativas.")
    
    with st.form("form_login"):
        username = st.text_input("Nome de usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            user = get_user(username)
            if user and user.get("password") == hash_password(password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user.get('role')
                st.success(f"Bem-vindo(a), {username}!")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

else:
    # Interface para usuários logados: Opções de Gestão
    option = st.radio(
        "Selecione uma função:",
        ["Dashboard Admin", "Cadastrar Novo Usuário", "Lista de Acessos"],
        horizontal=True
    )

    st.markdown("---")

    if option == "Dashboard Admin":
        st.subheader("Informações da Sessão")
        st.write(f"Você está logado com privilégios de: **{st.session_state.get('role')}**")
        st.write("A partir daqui você pode gerenciar o estoque nas outras abas do menu lateral.")

    elif option == "Cadastrar Novo Usuário":
        # Apenas Admins podem criar novos usuários
        if st.session_state.get('role') != 'admin':
            st.warning("⚠️ Apenas Administradores podem cadastrar novos perfis.")
        else:
            with st.form("form_cadastro"):
                new_user = st.text_input("Novo nome de usuário")
                new_pass = st.text_input("Senha", type="password")
                confirm = st.text_input("Confirme a senha", type="password")
                new_role = st.selectbox("Nível de Acesso", ["staff", "admin"])
                
                if st.form_submit_button("Registrar Usuário"):
                    if not new_user or not new_pass:
                        st.error("Preencha todos os campos.")
                    elif new_pass != confirm:
                        st.error("As senhas não coincidem.")
                    elif get_user(new_user):
                        st.error("Este nome de usuário já está em uso.")
                    else:
                        add_user(new_user, new_pass, role=new_role)
                        st.success(f"Usuário '{new_user}' criado com sucesso!")

    elif option == "Lista de Acessos":
        if st.session_state.get('role') != 'admin':
            st.warning("⚠️ Acesso restrito a administradores.")
        else:
            st.subheader("Usuários Ativos no Sistema")
            users = get_all_users()
            
            # Tabela simples de usuários
            import pandas as pd
            df_users = pd.DataFrame(users)
            if not df_users.empty:
                st.table(df_users[['username', 'role']])
            else:
                st.write("Nenhum usuário encontrado.")
