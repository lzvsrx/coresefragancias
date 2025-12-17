import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import add_user, get_user, get_all_users, check_user_login, safe_int

st.set_page_config(page_title="Admin - Cores e Fragrâncias", page_icon="🔐", layout="wide")

def load_css(file_name="style.css"):
    try:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except: pass

load_css("style.css")
st.title("🔐 Área Administrativa")
st.markdown("---")

if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

with st.sidebar:
    if st.session_state.get("logged_in"):
        st.success(f"✅ {st.session_state.get('username', 'User')}")
        if st.button("Sair"): 
            for k in ["logged_in", "username", "role"]: st.session_state.pop(k, None)
            st.rerun()
    else:
        st.info("🔒 Faça login")

if not st.session_state.get("logged_in"):
    with st.form("login"):
        user = st.text_input("Usuário")
        pwd = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if check_user_login(user, pwd):
                st.session_state.update({"logged_in": True, "username": user, "role": get_user(user)['role']})
                st.rerun()
            else: st.error("❌ Credenciais inválidas (admin/123)")
else:
    role = st.session_state.get('role', 'staff')
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Novo Usuário", "Lista"])
    
    with tab1:
        st.success(f"Logado: **{st.session_state['username']}** ({role.upper()})")
    
    with tab2:
        if role == 'admin':
            with st.form("new_user"):
                nuser = st.text_input("Novo usuário")
                npass = st.text_input("Senha", type="password")
                nrole = st.selectbox("Nível", ["staff", "admin"])
                if st.form_submit_button("Criar"):
                    if add_user(nuser, npass, nrole): st.success("✅ Criado!")
                    else: st.error("❌ Já existe")
        else: st.warning("👑 Apenas admin")
    
    with tab3:
        users = get_all_users()
        if users: st.dataframe(pd.DataFrame(users))
        else: st.info("Nenhum usuário")

st.caption(f"© {datetime.now().year} Cores e Fragrâncias")
