import streamlit as st
import os
from datetime import datetime, date
from utils.database import (
    add_produto, get_all_produtos, update_produto, delete_produto, get_produto_by_id,
    export_produtos_to_csv_content, import_produtos_from_csv_buffer, generate_stock_pdf_bytes,
    mark_produto_as_sold, MARCAS, ESTILOS, TIPOS, ASSETS_DIR
)

if not st.session_state.get("logged_in"):
    st.error("🔒 Acesso Restrito."); st.stop()

if 'edit_mode' not in st.session_state: st.session_state['edit_mode'] = False

def format_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def manage_list():
    st.title("🛠️ Gestão de Estoque")
    
    # Botões de Relatório
    c1, c2, c3 = st.columns(3)
    with c1: st.download_button("⬇️ Baixar CSV", export_produtos_to_csv_content().encode('utf-8'), "estoque.csv")
    with c2: 
        if st.button("⬇️ Gerar PDF"):
            st.download_button("Clique para Baixar PDF", generate_stock_pdf_bytes(), "relatorio.pdf")
    
    st.divider()
    produtos = get_all_produtos()
    for p in produtos:
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                path = os.path.join(ASSETS_DIR, p['foto']) if p['foto'] else ""
                if os.path.exists(path): st.image(path, width=100)
                else: st.caption("Sem foto")
            with col2:
                st.markdown(f"### {p['nome']}")
                st.write(f"ID: {p['id']} | Preço: {format_brl(p['preco'])} | **Qtd: {p['quantidade']}**")
                if p['quantidade'] > 0:
                    if st.button(f"💰 Vender 1 un.", key=f"v_{p['id']}"):
                        mark_produto_as_sold(p['id'], 1); st.rerun()
            with col3:
                if st.button("✏️", key=f"e_{p['id']}"):
                    st.session_state['edit_product_id'] = p['id']
                    st.session_state['edit_mode'] = True; st.rerun()
                if st.session_state['role'] == 'admin':
                    if st.button("🗑️", key=f"d_{p['id']}"):
                        delete_produto(p['id']); st.rerun()

# Fluxo de navegação
if st.session_state.get('edit_mode'):
    # (Inserir aqui a função show_edit_form do código anterior)
    pass 
else:
    manage_list()
