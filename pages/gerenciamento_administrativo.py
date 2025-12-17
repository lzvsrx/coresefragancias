import streamlit as st
import os
from utils.database import add_user, get_user, get_all_users, hash_password, delete_user

st.set_page_config(page_title="Administração")

if os.path.exists("style.css"):
    with open("style.css", encoding='utf-8') as f: st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("🔐 Área Administrativa")

if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

menu = st.selectbox("Ação", ["Login", "Cadastrar", "Gerenciar Usuários"])

if menu == "Login":
    user = st.text_input("Usuário")
    pw = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        u = get_user(user)
        if u and u['password'] == hash_password(pw):
            st.session_state["logged_in"] = True
            st.session_state["role"] = u['role']
            st.success("Logado!")
            st.rerun()
        else: st.error("Erro!")

elif menu == "Cadastrar":
    new_u = st.text_input("Novo Usuário")
    new_p = st.text_input("Senha", type="password")
    role = st.selectbox("Role", ["staff", "admin"])
    if st.button("Criar"):
        add_user(new_u, new_p, role)
        st.success("Criado!")

elif menu == "Gerenciar Usuários":
    if st.session_state.get("role") == "admin":
        for u in get_all_users():
            col1, col2 = st.columns([3, 1])
            col1.write(f"👤 {u['username']} ({u['role']})")
            if col2.button("Excluir", key=u['username']):
                delete_user(u['username'])
                st.rerun()
    else: st.error("Acesso apenas para Admins")
