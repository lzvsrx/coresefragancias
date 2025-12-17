# pages/gerenciamento_administrativo.py
import streamlit as st
import os
from utils.database import (
    add_user, get_user, get_all_users, hash_password,
    update_user_role, delete_user, create_tables
)

st.set_page_config(page_title="Área Administrativa", layout="wide")
create_tables()

# Estados de sessão
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = ""
if "role" not in st.session_state: st.session_state["role"] = "guest"

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except: pass

load_css()

st.title("🔐 Área Administrativa")
st.markdown("**Gerencie usuários, faça login ou cadastre novos administradores/funcionários**")

# Sidebar logout
if st.session_state["logged_in"]:
    st.sidebar.success(f"Logado: **{st.session_state['username']}** ({st.session_state['role']})")
    if st.sidebar.button("Sair"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = "guest"
        st.rerun()

option = st.selectbox("Escolha uma ação", ["🔑 Login", "➕ Cadastrar Usuário", "👥 Gerenciar Contas"])

# 1. LOGIN
if option == "🔑 Login":
    st.subheader("Login")
    username = st.text_input("Usuário", key="login_user")
    password = st.text_input("Senha", type="password", key="login_pass")
    
    if st.button("Entrar", type="primary"):
        if username and password:
            user = get_user(username)
            if user and hash_password(password) == user["password"]:
                st.success(f"✅ Bem-vindo, **{username}** ({user['role'].title()})!")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user["role"]
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos")
        else:
            st.error("Preencha todos os campos")
    
    st.info("**Admin padrão:** `admin` / `123`")

# 2. CADASTRO
elif option == "➕ Cadastrar Usuário":
    st.subheader("Criar Novo Usuário")
    col1, col2 = st.columns(2)
    
    with col1:
        new_username = st.text_input("Nome de usuário", key="reg_user")
        new_password = st.text_input("Senha", type="password", key="reg_pass")
    with col2:
        confirm_pass = st.text_input("Confirme senha", type="password", key="reg_conf")
        role = st.selectbox("Tipo", ["user", "staff", "admin"], 
                          format_func=lambda x: {"user": "👤 Normal", "staff": "🧑‍💼 Funcionário", "admin": "👑 Admin"}[x])
    
    if st.button("Criar", type="primary"):
        if not all([new_username, new_password, confirm_pass]):
            st.error("❌ Preencha todos os campos")
        elif new_password != confirm_pass:
            st.error("❌ Senhas não coincidem")
        elif get_user(new_username):
            st.error("❌ Usuário já existe")
        else:
            if add_user(new_username, new_password, role):
                st.success(f"✅ **{new_username}** criado como **{role.title()}**!")
                st.rerun()
            else:
                st.error("❌ Erro ao criar usuário")

# 3. GERENCIAR (APENAS ADMIN)
elif option == "👥 Gerenciar Contas":
    if not st.session_state["logged_in"] or st.session_state["role"] != "admin":
        st.error("🚫 **Apenas admins** podem gerenciar contas. Login: `admin` / `123`")
    else:
        st.subheader("Usuários Cadastrados")
        users = get_all_users()
        
        for user in users:
            col1, col2, col3, col4 = st.columns([3,1,1.2,1])
            with col1:
                role_emoji = {"admin": "👑", "staff": "🧑‍💼", "user": "👤"}[user["role"]]
                st.write(f"**{user['username']}** {role_emoji} ({user['role'].title()})")
            with col2:
                if st.button("✏️", key=f"edit_{user['id']}"):
                    st.session_state["edit_user"] = user["id"]
                    st.rerun()
            with col3:
                if st.button("🔄", key=f"role_{user['id']}"):
                    new_role = "admin" if user["role"] != "admin" else "user"
                    if update_user_role(user["id"], new_role):
                        st.success(f"Role alterado para {new_role}")
                        st.rerun()
            with col4:
                if st.button("🗑️", key=f"del_{user['id']}"):
                    if delete_user(user["id"]):
                        st.success(f"**{user['username']}** excluído")
                        st.rerun()
        
        # Edição avançada
        if st.session_state.get("edit_user"):
            user_edit = next((u for u in users if u["id"] == st.session_state["edit_user"]), None)
            if user_edit:
                new_role = st.selectbox("Novo role", ["user", "staff", "admin"], 
                                      index=["user", "staff", "admin"].index(user_edit["role"]))
                if st.button("Salvar"):
                    update_user_role(user_edit["id"], new_role)
                    del st.session_state["edit_user"]
                    st.rerun()
