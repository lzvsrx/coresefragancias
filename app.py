import streamlit as st
import os
from utils.database import create_tables, get_all_produtos
from datetime import datetime

st.set_page_config(page_title="Cores e Fragrâncias", page_icon="🌸", layout="wide")

create_tables()

if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = ""
if "role" not in st.session_state: st.session_state["role"] = "guest"

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css()

st.title("🌸 Cores e Fragrâncias by Berenice")
st.markdown("---")

if st.session_state["logged_in"]:
    st.markdown("### 📊 Dashboard de Resumo")
    produtos = get_all_produtos()
    total_itens = sum(p['quantidade'] for p in produtos)
    total_valor = sum(p['preco'] * p['quantidade'] for p in produtos)
    itens_alerta = [p for p in produtos if 0 < p['quantidade'] <= 3]

    col1, col2, col3 = st.columns(3)
    col1.metric("Peças em Estoque", f"{total_itens} un")
    col2.metric("Valor Total", f"R$ {total_valor:,.2f}")
    col3.metric("Alertas (Estoque Baixo)", f"{len(itens_alerta)} itens")

    if itens_alerta:
        with st.expander("⚠️ Ver itens para reposição"):
            for item in itens_alerta:
                st.write(f"- {item['nome']}: apenas **{item['quantidade']}** un.")
else:
    st.info("👋 Bem-vindo! Por favor, faça login na Área Administrativa para gerenciar o sistema.")

st.sidebar.markdown(f"**Usuário:** {st.session_state['username'] or 'Visitante'}")
