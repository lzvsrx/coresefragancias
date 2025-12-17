# main.py
import streamlit as st
from datetime import datetime
from utils.database import create_tables, get_all_produtos

st.set_page_config(page_title="Cores e Fragrâncias", page_icon="🌸", layout="wide")

create_tables()

st.title("🌸 Cores e Fragrâncias by Berenice")
st.markdown("---")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "role" not in st.session_state:
    st.session_state["role"] = "guest"

st.write("Use o menu lateral para navegar entre as páginas:")

col1, col2 = st.columns(2)
with col1:
    st.metric("Produtos cadastrados", len(get_all_produtos()))
with col2:
    st.metric("Status", "Online")

st.caption(f"© {datetime.now().year} Cores e Fragrâncias")
