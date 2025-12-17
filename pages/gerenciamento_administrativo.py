import streamlit as st
import os
from utils.database import add_user, get_user, get_all_users, hash_password

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

st.title("🔐 Área Administrativa")

if st.session_state["logged_in"]:
    st.sidebar.success(f"Usuário: {st.session_state['username']}")
    if st.sidebar.button("Sair/Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

    tab1, tab2 = st.tabs(["Controle de Acesso", "Info Sistema"])
    
    with tab1:
        if st.session_state.get('role') == 'admin':
            st.subheader("Cadastrar Novo Membro")
            with st.form("reg_form"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                r = st.selectbox("Nível", ["staff", "admin"])
                if st.form_submit_button("Criar Conta"):
                    if get_user(u): st.error("Usuário já existe!")
                    else:
                        add_user(u, p, role=r)
                        st.success("Criado!")
            
            st.divider()
            st.subheader("Usuários Ativos")
            for user in get_all_users():
                st.text(f"👤 {user['username']} - Nível: {user['role']}")
        else:
            st.warning("Apenas administradores podem gerenciar usuários.")
else:
    # Tela de Login
    with st.container(border=True):
        user_in = st.text_input("Usuário")
        pass_in = st.text_input("Senha", type="password")
        if st.button("Acessar Painel"):
            user_db = get_user(user_in)
            if user_db and user_db['password'] == hash_password(pass_in):
                st.session_state["logged_in"] = True
                st.session_state["username"] = user_db['username']
                st.session_state["role"] = user_db['role']
                st.rerun()
            else:
                st.error("Credenciais inválidas")
