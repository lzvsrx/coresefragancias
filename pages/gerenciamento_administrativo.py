import streamlit as st
import os
# Importando as funções do seu database.py
from utils.database import add_user, get_user, get_all_users, hash_password

# --- CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA CHAMADA) ---
st.set_page_config(page_title="Área Administrativa - Cores e Fragrâncias", layout="wide")

# --- FUNÇÃO CSS INTEGRADA ---
def load_css(file_name="style.css"):
    """Carrega e aplica o CSS personalizado, forçando a codificação UTF-8."""
    if os.path.exists(file_name):
        try:
            with open(file_name, encoding='utf-8') as f: 
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar CSS: {e}")

load_css() # Chama o CSS

st.title("🔐 Área Administrativa")

# Inicializa o estado de login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Barra lateral com Status e Logout
if st.session_state.get("logged_in"):
    st.sidebar.success(f"Logado como: **{st.session_state.get('username')}**")
    st.sidebar.info(f"Cargo: {st.session_state.get('role')}")
    if st.sidebar.button("Sair/Logout"):
        st.session_state["logged_in"] = False
        st.session_state.pop("username", None)
        st.session_state.pop("role", None)
        st.rerun()

st.markdown("Gerencie acessos ou faça login para liberar funções restritas.")

option = st.selectbox("Escolha uma ação", ["Login", "Cadastrar Novo Usuário", "Gerenciar Contas (Admins)"])

# --- LÓGICA DE LOGIN ---
if option == "Login":
    with st.form("form_login"):
        username = st.text_input("Nome de usuário")
        password = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            user = get_user(username)
            if user and user.get("password") == hash_password(password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user.get('role')
                st.success(f"Bem-vindo(a), {username}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

# --- LÓGICA DE CADASTRO ---
elif option == "Cadastrar Novo Usuário":
    # Apenas logados (ou admin) podem cadastrar, dependendo da sua regra. 
    # Aqui permitiremos o cadastro inicial para não travar seu sistema.
    with st.form("form_registro"):
        new_username = st.text_input("Novo nome de usuário")
        new_password = st.text_input("Senha", type="password")
        confirm = st.text_input("Confirme a senha", type="password")
        role = st.selectbox("Papel do usuário", ["staff", "admin"])
        
        if st.form_submit_button("Finalizar Cadastro"):
            if not new_username or not new_password:
                st.error("Preencha todos os campos.")
            elif new_password != confirm:
                st.error("As senhas não coincidem.")
            elif get_user(new_username):
                st.error("Este nome de usuário já está em uso.")
            else:
                add_user(new_username, new_password, role=role)
                st.success(f"Usuário '{new_username}' criado! Faça login.")

# --- LÓGICA DE GERENCIAMENTO ---
elif option == "Gerenciar Contas (Admins)":
    if not st.session_state.get('logged_in') or st.session_state.get('role') != 'admin':
        st.error('Acesso restrito. Apenas administradores logados podem ver esta lista.')
    else:
        st.subheader('Contas Ativas no Sistema')
        users = get_all_users()
        if users:
            for u in users:
                st.code(f"Usuário: {u.get('username')} | Cargo: {u.get('role')}")
        else:
            st.info("Nenhum usuário listado.")
