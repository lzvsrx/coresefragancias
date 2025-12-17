import streamlit as st
from utils.database import add_user, get_user, hash_password, get_all_users

st.title("🔐 Administração")

if not st.session_state.logged_in:
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            user = get_user(u)
            if user and user['password'] == hash_password(p):
                st.session_state.update({"logged_in": True, "username": u, "role": user['role']})
                st.rerun()
            else: st.error("Erro de login.")
else:
    st.write(f"Logado como {st.session_state.username}")
    if st.button("Logout"): 
        st.session_state.logged_in = False; st.rerun()
    
    if st.session_state.role == 'admin':
        st.subheader("Novos Usuários")
        # Formulário de add_user simplificado aqui

