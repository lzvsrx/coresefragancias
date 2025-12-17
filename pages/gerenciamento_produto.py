import streamlit as st
import os
from datetime import datetime, date
from utils.database import (
    add_produto, get_all_produtos, update_produto, delete_produto, get_produto_by_id,
    export_produtos_to_csv_content, import_produtos_from_csv_buffer, generate_stock_pdf_bytes,
    mark_produto_as_sold,
    MARCAS, ESTILOS, TIPOS, ASSETS_DIR
)

# --- CONFIGURAÇÃO DA PÁGINA ---
def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

if not st.session_state.get("logged_in"):
    st.error("🔒 **Acesso Restrito.** Por favor, faça login na Área Administrativa.")
    st.stop()
    
if 'edit_mode' not in st.session_state: st.session_state['edit_mode'] = False
if 'edit_product_id' not in st.session_state: st.session_state['edit_product_id'] = None

def format_to_brl(value):
    try:
        return f"R$ {float(value):_.2f}".replace('.', 'X').replace('_', '.').replace('X', ',')
    except: return "R$ 0,00"

# --- FORMULÁRIO DE CADASTRO ---
def add_product_form():
    st.subheader("➕ Adicionar Novo Produto")
    with st.form("add_product_form", clear_on_submit=True):
        nome = st.text_input("Nome do Produto", max_chars=150)
        col1, col2 = st.columns([3, 1]) 
        with col1:
            marca = st.selectbox("📝 Marca", options=['Selecionar'] + MARCAS)
            estilo = st.selectbox("Estilo", ['Selecionar'] + ESTILOS)
            tipo = st.selectbox("🏷️ Tipo", options=['Selecionar'] + TIPOS)
            preco = st.number_input("Preço (R$)", min_value=0.01, format="%.2f")
            quantidade = st.number_input("Quantidade Inicial", min_value=1, step=1)
            data_validade = st.date_input("🗓️ Validade", value=None, min_value=date.today())
        with col2:
            foto = st.file_uploader("🖼️ Foto", type=['png', 'jpg', 'jpeg'])

        if st.form_submit_button("Cadastrar"):
            if not nome or preco <= 0 or marca == 'Selecionar':
                st.error("Preencha os campos obrigatórios.")
            else:
                photo_name = None
                if foto:
                    photo_name = f"{int(datetime.now().timestamp())}_{foto.name}"
                    with open(os.path.join(ASSETS_DIR, photo_name), "wb") as f:
                        f.write(foto.getbuffer())
                
                validade_iso = data_validade.isoformat() if data_validade else None
                add_produto(nome, preco, quantidade, marca, estilo, tipo, photo_name, validade_iso)
                st.success("Produto cadastrado!")
                st.rerun()

# --- FORMULÁRIO DE EDIÇÃO ---
def show_edit_form():
    produto = get_produto_by_id(st.session_state['edit_product_id'])
    if not produto: 
        st.session_state['edit_mode'] = False
        st.rerun()

    st.subheader(f"✏️ Editando: {produto['nome']}")
    with st.form("edit_form"):
        nome = st.text_input("Nome", value=produto['nome'])
        preco = st.number_input("Preço", value=float(produto['preco']), format="%.2f")
        quantidade = st.number_input("Estoque", value=int(produto['quantidade']), min_value=0)
        
        # Correção de índices para Selectbox
        m_idx = MARCAS.index(produto['marca']) if produto['marca'] in MARCAS else 0
        marca = st.selectbox("Marca", MARCAS, index=m_idx)
        
        uploaded = st.file_uploader("Trocar Foto", type=["jpg","png","jpeg"])
        
        col1, col2 = st.columns(2)
        if col1.form_submit_button("Salvar"):
            final_photo = produto['foto']
            if uploaded:
                final_photo = f"upd_{int(datetime.now().timestamp())}_{uploaded.name}"
                with open(os.path.join(ASSETS_DIR, final_photo), "wb") as f:
                    f.write(uploaded.getbuffer())
            
            update_produto(produto['id'], nome, preco, quantidade, marca, produto['estilo'], produto['tipo'], final_photo, produto['data_validade'])
            st.session_state['edit_mode'] = False
            st.rerun()
        if col2.form_submit_button("Cancelar"):
            st.session_state['edit_mode'] = False
            st.rerun()

# --- LISTAGEM E AÇÕES ---
def manage_products_list_actions():
    st.title("🛠️ Gerenciar Estoque")
    
    # Downloads e Uploads
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇️ Exportar CSV", export_produtos_to_csv_content().encode('utf-8'), "estoque.csv", "text/csv")
    with c2:
        up_csv = st.file_uploader("⬆️ Importar CSV", type=['csv'])
        if up_csv and st.button("Processar"):
            import_produtos_from_csv_buffer(up_csv)
            st.rerun()
    with c3:
        if st.button("⬇️ Gerar PDF"):
            st.download_button("Baixar PDF", generate_stock_pdf_bytes(), "relatorio.pdf", "application/pdf")

    st.divider()
    
    # FILTRO: Mostrar tudo para o admin não "perder" nenhum produto de vista
    produtos = get_all_produtos(include_sold=True) 
    
    for p in produtos:
        with st.container(border=True):
            col_img, col_info, col_btn = st.columns([1, 3, 1])
            
            with col_img:
                if p['foto'] and os.path.exists(os.path.join(ASSETS_DIR, p['foto'])):
                    st.image(os.path.join(ASSETS_DIR, p['foto']), width=100)
                else: st.caption("Sem foto")

            with col_info:
                st.markdown(f"**{p['nome']}** (ID: {p['id']})")
                st.write(f"Estoque: {p['quantidade']} | {format_to_brl(p['preco'])}")
                if p['quantidade'] > 0:
                    if st.button(f"💰 Vender 1 un.", key=f"sell_{p['id']}"):
                        mark_produto_as_sold(p['id'], 1)
                        st.rerun()
                else:
                    st.error("Esgotado")

            with col_btn:
                if st.button("✏️", key=f"ed_{p['id']}"):
                    st.session_state['edit_product_id'] = p['id']
                    st.session_state['edit_mode'] = True
                    st.rerun()
                if st.session_state.get('role') == 'admin':
                    if st.button("🗑️", key=f"del_{p['id']}"):
                        delete_produto(p['id'])
                        st.rerun()

# Fluxo
if st.session_state['edit_mode']:
    show_edit_form()
else:
    menu = st.sidebar.radio("Navegação", ["Lista de Produtos", "Adicionar Novo"])
    if menu == "Adicionar Novo": add_product_form()
    else: manage_products_list_actions()
