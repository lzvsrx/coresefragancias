import streamlit as st
import os
from utils.database import add_user, get_user, get_all_users, hash_password, delete_user

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(page_title="Administração")
load_css()

st.title("🔐 Administração")

if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    st.sidebar.success(f"Logado como {st.session_state['username']}")
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

menu = st.selectbox("Menu", ["Login", "Cadastrar Novo", "Gerenciar Contas"])

if menu == "Login":
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Acessar"):
        user = get_user(u)
        if user and user['password'] == hash_password(p):
            st.session_state["logged_in"] = True
            st.session_state["username"] = u
            st.session_state["role"] = user['role']
            st.rerun()
        else: st.error("Dados inválidos.")

elif menu == "Cadastrar Novo":
    with st.form("cad"):
        nu = st.text_input("Usuário")
        np = st.text_input("Senha", type="password")
        nr = st.selectbox("Role", ["staff", "admin"])
        if st.form_submit_button("Criar"):
            add_user(nu, np, nr)
            st.success("Criado!")

elif menu == "Gerenciar Contas":
    if st.session_state.get("role") == "admin":
        for u in get_all_users():
            c1, c2 = st.columns([3, 1])
            c1.write(f"👤 {u['username']} ({u['role']})")
            if u['username'] != "admin" and c2.button("Excluir", key=u['username']):
                delete_user(u['username'])
                st.rerun()
    else: st.error("Apenas administradores.")
