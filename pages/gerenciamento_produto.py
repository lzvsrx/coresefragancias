import streamlit as st
from datetime import date
from utils.database import *

st.set_page_config(page_title="Produtos", page_icon="🛠️", layout="wide")
load_css()

if not st.session_state.get("logged_in"):
    st.error("🔒 Login necessário"); st.stop()

if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False

def add_product():
    st.subheader("➕ Novo Produto")
    with st.form("new_prod"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome")
            marca = st.selectbox("Marca", [''] + MARCAS)
            tipo = st.selectbox("Tipo", [''] + TIPOS)
            preco = st.number_input("Preço", min_value=0.01)
        with col2:
            qtd = st.number_input("Qtd", min_value=0)
            foto = st.file_uploader("Foto", type=['jpg', 'png'])
        
        if st.form_submit_button("Salvar"):
            if nome and marca and tipo and preco > 0:
                photo_name = None
                if foto:
                    photo_name = f"{int(datetime.now().timestamp())}_{foto.name}"
                    with open(os.path.join(ASSETS_DIR, photo_name), "wb") as f: f.write(foto.getbuffer())
                add_produto(nome, preco, qtd, marca, '', tipo, photo_name, None)
                st.success("✅ Salvo!"); st.rerun()
            else: st.error("❌ Preencha tudo")

if st.session_state.edit_mode:
    # EDIÇÃO (SIMPLIFICADA)
    st.subheader("✏️ Editar")
    st.button("Cancelar", on_click=lambda: setattr(st.session_state, 'edit_mode', False) or st.rerun())
else:
    action = st.sidebar.radio("Ação", ["Listar", "Novo"])
    if action == "Novo": add_product()
    else:
        for p in get_all_produtos():
            with st.container(border=True):
                st.write(f"**{p['nome']}** - R${p['preco']} (Qtd: {p['quantidade']})")
                col1, col2 = st.columns(2)
                col1.button("Editar", key=f"ed{p['id']}", on_click=lambda id=p['id']: setattr(st.session_state, 'edit_product_id', id) or setattr(st.session_state, 'edit_mode', True) or st.rerun())
                if st.session_state.get('role') == 'admin': col2.button("Deletar", key=f"del{p['id']}", on_click=lambda id=p['id']: delete_produto(id) or st.rerun())
