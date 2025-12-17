import streamlit as st
import os
from datetime import datetime, date
from utils.database import (
    add_produto, get_all_produtos, update_produto, delete_produto, get_produto_by_id,
    export_produtos_to_csv_content, import_produtos_from_csv_buffer, generate_stock_pdf_bytes,
    mark_produto_as_sold,
    MARCAS, ESTILOS, TIPOS, ASSETS_DIR
)

# --- CONFIGURAÇÃO E CSS ---
def load_css(file_name="style.css"):
    """Carrega e aplica o CSS personalizado, forçando a codificação UTF-8."""
    if os.path.exists(file_name):
        with open(file_name, encoding='utf-8') as f: 
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# --- VERIFICAÇÃO DE SEGURANÇA ---
if not st.session_state.get("logged_in"):
    st.error("🔒 **Acesso Restrito.** Por favor, faça login na Área Administrativa.")
    st.stop()
    
# Inicialização de estado para navegação interna
if 'edit_mode' not in st.session_state: st.session_state['edit_mode'] = False
if 'edit_product_id' not in st.session_state: st.session_state['edit_product_id'] = None

# --- HELPER DE FORMATAÇÃO ---
def format_to_brl(value):
    """Formata um float para string no formato R$ 1.234,56."""
    try:
        return f"R$ {float(value):_.2f}".replace('.', 'X').replace('_', '.').replace('X', ',')
    except (ValueError, TypeError):
        return "R$ N/A"

# --- MÓDULO 1: CADASTRO DE PRODUTO ---
def add_product_form():
    st.subheader("➕ Adicionar Novo Produto")
    
    with st.form("add_product_form", clear_on_submit=True):
        nome = st.text_input("Nome do Produto", max_chars=150)
        
        col1, col2 = st.columns([2, 1]) 

        with col1:
            marca = st.selectbox("📝 Marca", options=['Selecionar'] + MARCAS)
            tipo = st.selectbox("🏷️ Tipo", options=['Selecionar'] + TIPOS)
            estilo = st.selectbox("👤 Estilo", options=['Selecionar'] + ESTILOS)
            preco = st.number_input("Preço de Venda (R$)", min_value=0.0, format="%.2f", step=0.50)
            quantidade = st.number_input("Quantidade Inicial", min_value=1, step=1)
            data_validade = st.date_input("🗓️ Validade (Opcional)", value=None, min_value=date.today())
            
        with col2:
            st.markdown("##### Foto do Produto")
            foto = st.file_uploader("Upload da Imagem", type=['png', 'jpg', 'jpeg'])
            if foto:
                st.image(foto, caption="Pré-visualização", use_container_width=True)

        submitted = st.form_submit_button("💾 Salvar Produto")

        if submitted:
            if not nome or preco <= 0 or marca == 'Selecionar' or tipo == 'Selecionar':
                st.error("Campos obrigatórios: Nome, Preço, Marca e Tipo.")
                return
            
            photo_name = None
            if foto:
                photo_name = f"{int(datetime.now().timestamp())}_{foto.name}"
                with open(os.path.join(ASSETS_DIR, photo_name), "wb") as f:
                    f.write(foto.getbuffer())
            
            try:
                validade_iso = data_validade.isoformat() if data_validade else None
                add_produto(nome, preco, quantidade, marca, estilo, tipo, photo_name, validade_iso)
                st.success(f"✅ Produto '{nome}' cadastrado!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro no banco: {e}")

# --- MÓDULO 2: EDIÇÃO DE PRODUTO ---
def show_edit_form():
    produto_id = st.session_state.get('edit_product_id')
    p = get_produto_by_id(produto_id)

    if not p:
        st.error("Produto não encontrado."); st.session_state['edit_mode'] = False; st.rerun()

    st.subheader(f"✏️ Editando: {p['nome']}")
    
    with st.form("edit_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            novo_nome = st.text_input("Nome", value=p['nome'])
            novo_preco = st.number_input("Preço", value=float(p['preco']), format="%.2f")
            nova_qtd = st.number_input("Quantidade", value=int(p['quantidade']), min_value=0)
            nova_marca = st.selectbox("Marca", MARCAS, index=MARCAS.index(p['marca']) if p['marca'] in MARCAS else 0)
            novo_tipo = st.selectbox("Tipo", TIPOS, index=TIPOS.index(p['tipo']) if p['tipo'] in TIPOS else 0)
        
        with col2:
            st.info(f"Foto Atual: {p['foto'] or 'Sem foto'}")
            nova_foto = st.file_uploader("Trocar Foto", type=['jpg', 'png'])

        c1, c2 = st.columns(2)
        if c1.form_submit_button("✅ Confirmar Alterações"):
            img_final = p['foto']
            if nova_foto:
                img_final = f"edit_{int(datetime.now().timestamp())}_{nova_foto.name}"
                with open(os.path.join(ASSETS_DIR, img_final), "wb") as f:
                    f.write(nova_foto.getbuffer())
            
            update_produto(produto_id, novo_nome, novo_preco, nova_qtd, nova_marca, p['estilo'], novo_tipo, img_final, p['data_validade'])
            st.session_state['edit_mode'] = False
            st.rerun()
        
        if c2.form_submit_button("❌ Cancelar"):
            st.session_state['edit_mode'] = False; st.rerun()

# --- MÓDULO 3: LISTAGEM E RELATÓRIOS ---
def manage_products_list_actions():
    st.title("🛠️ Gerenciar Produtos")
    
    # --- Barra de Ferramentas (Relatórios) ---
    with st.expander("📊 Relatórios e Integração", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.download_button("📥 Exportar CSV", export_produtos_to_csv_content().encode('utf-8'), "estoque.csv", "text/csv")
        
        pdf_btn = c2.button("📑 Gerar PDF de Estoque")
        if pdf_btn:
            st.download_button("Clique para Baixar PDF", generate_stock_pdf_bytes(), "relatorio_estoque.pdf")
            
        csv_file = c3.file_uploader("📤 Importar CSV", type=['csv'])
        if csv_file and c3.button("Processar CSV"):
            count = import_produtos_from_csv_buffer(csv_file)
            st.success(f"{count} produtos importados!"); st.rerun()

    st.markdown("---")
    
    produtos = get_all_produtos()
    if not produtos:
        st.info("Nenhum produto em estoque.")
        return

    total_financeiro = 0.0
    for p in produtos:
        pid = p['id']
        valor_item = float(p['preco']) * int(p['quantidade'])
        total_financeiro += valor_item

        with st.container(border=True):
            col_img, col_txt, col_btn = st.columns([1, 3, 1])
            
            with col_img:
                path = os.path.join(ASSETS_DIR, p['foto']) if p['foto'] else ""
                if os.path.exists(path): st.image(path, use_container_width=True)
                else: st.markdown("🖼️\nSem Foto")
            
            with col_txt:
                st.markdown(f"### {p['nome']} <small>(ID {pid})</small>", unsafe_allow_html=True)
                st.write(f"**{format_to_brl(p['preco'])}** | Estoque: **{p['quantidade']}** | Subtotal: {format_to_brl(valor_item)}")
                st.caption(f"{p['marca']} • {p['tipo']} • Validade: {p['data_validade'] or '-'}")
                
                if p['quantidade'] > 0:
                    if st.button(f"💰 Vender 1 un.", key=f"v_{pid}"):
                        mark_produto_as_sold(pid, 1); st.rerun()
            
            with col_btn:
                if st.button("✏️ Editar", key=f"ed_{pid}", use_container_width=True):
                    st.session_state['edit_product_id'] = pid
                    st.session_state['edit_mode'] = True; st.rerun()
                
                if st.session_state.get('role') == 'admin':
                    if st.button("🗑️ Excluir", key=f"del_{pid}", use_container_width=True):
                        delete_produto(pid); st.rerun()

    st.sidebar.metric("Valor Total em Estoque", format_to_brl(total_financeiro))

# --- FLUXO PRINCIPAL ---
if st.session_state['edit_mode']:
    show_edit_form()
else:
    menu = st.sidebar.radio("Navegação Interna", ["Listar e Ações", "Cadastrar Novo"])
    if menu == "Cadastrar Novo": add_product_form()
    else: manage_products_list_actions()
