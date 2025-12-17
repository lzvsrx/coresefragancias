import streamlit as st
import os
from datetime import datetime, date
from typing import Optional

# Protege TODAS as importações com fallback
try:
    from utils.database import (
        add_produto, get_all_produtos, update_produto, delete_produto, get_produto_by_id,
        export_produtos_to_csv_content, import_produtos_from_csv_buffer, generate_stock_pdf_bytes,
        mark_produto_as_sold, MARCAS, ESTILOS, TIPOS, ASSETS_DIR
    )
except ImportError as e:
    st.error(f"❌ Erro crítico no database: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Falha ao carregar módulos: {e}")
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA (PRIMEIRO!) ---
st.set_page_config(
    page_title="Gerenciar Produtos - Cores e Fragrâncias",
    page_icon="🛠️",
    layout="wide"
)

# --- FUNÇÕES AUXILIARES SEGURAS ---
def load_css(file_name="style.css"):
    """Carrega CSS silenciosamente."""
    try:
        if os.path.exists(file_name):
            with open(file_name, encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except:
        pass

def format_to_brl(value):
    """Formatação BRL segura."""
    try:
        num = float(value)
        if num <= 0: return "R$ 0,00"
        formatted = f"{num:_.2f}".replace('.', 'X').replace('_', '.').replace('X', ',')
        return f"R$ {formatted}"
    except:
        return "R$ N/A"

def safe_int(value, default=0):
    try: return int(value)
    except: return default

def safe_float(value, default=0.0):
    try: return float(value)
    except: return default

# Carrega CSS
load_css("style.css")

# --- VERIFICAÇÃO DE SEGURANÇA ---
if not st.session_state.get("logged_in", False):
    st.error("🔒 **Acesso Restrito.** Faça login na Área Administrativa.")
    st.stop()

# Inicialização segura de estados
if 'edit_mode' not in st.session_state: st.session_state['edit_mode'] = False
if 'edit_product_id' not in st.session_state: st.session_state['edit_product_id'] = None
if 'role' not in st.session_state: st.session_state['role'] = 'staff'

st.title("🛠️ Gerenciar Produtos")
st.markdown("---")

# --- MÓDULO 1: CADASTRO ---
def add_product_form():
    st.subheader("➕ Adicionar Novo Produto")
    
    with st.form("add_product_form", clear_on_submit=True):
        col_main, col_photo = st.columns([2, 1])
        
        with col_main:
            nome = st.text_input("Nome do Produto", max_chars=150, help="Nome completo do produto")
            preco = st.number_input("💰 Preço (R$)", min_value=0.01, format="%.2f", step=0.50)
            quantidade = st.number_input("📦 Quantidade", min_value=0, step=1, value=1)
            marca = st.selectbox("🏷️ Marca", ['Selecionar'] + MARCAS)
            estilo = st.selectbox("🎨 Estilo", ['Selecionar'] + ESTILOS)
            tipo = st.selectbox("📋 Tipo", ['Selecionar'] + TIPOS)
            data_validade = st.date_input("📅 Validade", value=None, min_value=date.today())
        
        with col_photo:
            st.markdown("### 📸 Foto")
            foto = st.file_uploader("Escolha imagem", type=['png', 'jpg', 'jpeg'])
            if foto:
                st.image(foto, caption="Pré-visualização", width=200)
        
        submitted = st.form_submit_button("💾 Cadastrar", use_container_width=True)
        
        if submitted:
            # Validações
            if not nome or preco <= 0 or marca == 'Selecionar' or tipo == 'Selecionar':
                st.error("❌ **Obrigatório:** Nome, Preço > 0, Marca e Tipo")
                return
            
            try:
                # Salva foto
                photo_name = None
                if foto:
                    photo_name = f"{int(datetime.now().timestamp())}_{foto.name}"
                    with open(os.path.join(ASSETS_DIR, photo_name), "wb") as f:
                        f.write(foto.getbuffer())
                
                # Salva no banco
                validade_iso = data_validade.isoformat() if data_validade else None
                new_id = add_produto(nome, preco, quantidade, marca, estilo, tipo, photo_name, validade_iso)
                st.success(f"🎉 **{nome}** cadastrado! ID: **{new_id}**")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro: {str(e)[:100]}")

# --- MÓDULO 2: EDIÇÃO ---
def show_edit_form():
    produto_id = st.session_state.get('edit_product_id')
    if not produto_id:
        st.error("❌ ID inválido")
        st.session_state['edit_mode'] = False
        st.rerun()
    
    try:
        produto = get_produto_by_id(produto_id)
        if not produto:
            st.error("❌ Produto não encontrado")
            st.session_state['edit_mode'] = False
            st.rerun()
    except:
        st.error("❌ Erro ao buscar produto")
        st.session_state['edit_mode'] = False
        st.rerun()

    st.subheader(f"✏️ Editando: **{produto.get('nome', 'N/A')}** (ID {produto_id})")
    
    with st.form(f"edit_form_{produto_id}", clear_on_submit=False):
        col_main, col_photo = st.columns([2, 1])
        
        with col_main:
            novo_nome = st.text_input("Nome", value=produto.get('nome', ''))
            novo_preco = st.number_input("Preço", value=safe_float(produto.get('preco', 0.0)), format="%.2f")
            nova_qtd = st.number_input("Quantidade", value=safe_int(produto.get('quantidade', 0)), min_value=0)
            
            # Selectbox seguros
            marca_idx = next((i for i, m in enumerate(MARCAS) if m == produto.get('marca')), 0)
            tipo_idx = next((i for i, t in enumerate(TIPOS) if t == produto.get('tipo')), 0)
            estilo_idx = next((i for i, e in enumerate(ESTILOS) if e == produto.get('estilo')), 0)
            
            nova_marca = st.selectbox("Marca", MARCAS, index=marca_idx)
            novo_tipo = st.selectbox("Tipo", TIPOS, index=tipo_idx)
            novo_estilo = st.selectbox("Estilo", ESTILOS, index=estilo_idx)
            
            nova_validade = st.date_input("Validade", value=None)
        
        with col_photo:
            st.info(f"Foto atual: {produto.get('foto', 'Nenhuma')}")
            nova_foto = st.file_uploader("🆕 Nova foto", type=['png', 'jpg', 'jpeg'])
            if nova_foto:
                st.image(nova_foto, width=150)
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.form_submit_button("✅ Salvar", use_container_width=True):
            try:
                # Remove foto antiga se nova
                foto_final = produto.get('foto')
                if nova_foto:
                    if foto_final and os.path.exists(os.path.join(ASSETS_DIR, foto_final)):
                        try: os.remove(os.path.join(ASSETS_DIR, foto_final))
                        except: pass
                    foto_final = f"edit_{int(datetime.now().timestamp())}_{nova_foto.name}"
                    with open(os.path.join(ASSETS_DIR, foto_final), "wb") as f:
                        f.write(nova_foto.getbuffer())
                
                validade_iso = nova_validade.isoformat() if nova_validade else produto.get('data_validade')
                update_produto(produto_id, novo_nome, novo_preco, nova_qtd, nova_marca, novo_estilo, novo_tipo, foto_final, validade_iso)
                st.success("✅ Produto atualizado!")
                st.session_state['edit_mode'] = False
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao atualizar: {str(e)[:100]}")
        
        if col_btn2.form_submit_button("❌ Cancelar", use_container_width=True):
            st.session_state['edit_mode'] = False
            st.rerun()

# --- MÓDULO 3: LISTAGEM ---
def manage_products_list_actions():
    st.subheader("📋 Produtos Cadastrados")
    
    # Relatórios
    col1, col2, col3 = st.columns(3)
    with col1:
        csv_content = export_produtos_to_csv_content()
        st.download_button(
            "📥 CSV Completo", 
            csv_content.encode('utf-8'), 
            f"estoque_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )
    
    with col2:
        if st.button("📑 PDF Estoque Ativo"):
            try:
                pdf_bytes = generate_stock_pdf_bytes()
                st.download_button(
                    "⬇️ Baixar PDF", 
                    pdf_bytes, 
                    f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    "application/pdf"
                )
            except:
                st.error("❌ Erro ao gerar PDF")
    
    with col3:
        csv_file = st.file_uploader("📤 Importar CSV", type='csv')
        if csv_file and st.button("🚀 Processar"):
            try:
                count = import_produtos_from_csv_buffer(csv_file)
                st.success(f"✅ {count} produtos importados!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro importação: {e}")
    
    st.markdown("---")
    
    try:
        produtos = get_all_produtos(include_sold=True)
    except:
        produtos = []
    
    if not produtos:
        st.info("📦 Nenhum produto cadastrado.")
        return
    
    total_valor = 0.0
    for produto in produtos:
        try:
            pid = safe_int(produto.get('id'))
            preco = safe_float(produto.get('preco'))
            qtd = safe_int(produto.get('quantidade'))
            valor_item = preco * qtd
            total_valor += valor_item
            
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 4, 1])
                
                # Foto
                with col1:
                    foto_path = os.path.join(ASSETS_DIR, produto.get('foto', '')) if produto.get('foto') else None
                    if foto_path and os.path.exists(foto_path):
                        st.image(foto_path, width=80)
                    else:
                        st.info("📷")
                
                # Detalhes
                with col2:
                    st.markdown(f"**{produto.get('nome', 'N/A')}**")
                    st.caption(f"ID: {pid} | {produto.get('marca', 'N/A')} • {produto.get('tipo', 'N/A')}")
                    st.write(f"**{format_to_brl(preco)}** | Qtd: **{qtd}** | **Total: {format_to_brl(valor_item)}**")
                
                # Ações
                with col3:
                    if qtd > 0:
                        if st.button("💰 Vender", key=f"sell_{pid}"):
                            try:
                                mark_produto_as_sold(pid, 1)
                                st.success("✅ Venda registrada!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ {e}")
                    
                    if st.button("✏️", key=f"edit_{pid}"):
                        st.session_state['edit_product_id'] = pid
                        st.session_state['edit_mode'] = True
                        st.rerun()
                    
                    if st.session_state.get('role') == 'admin':
                        if st.button("🗑️", key=f"del_{pid}"):
                            try:
                                delete_produto(pid)
                                st.success("🗑️ Excluído!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ {e}")
        except:
            continue
    
    st.sidebar.success(f"💰 **R$ {format_to_brl(total_valor)}**")

# --- FLUXO PRINCIPAL ---
st.sidebar.title("🛠️ Navegação")
action = st.sidebar.radio("Escolha:", ["📋 Listar Produtos", "➕ Novo Produto"])

if st.session_state.get('edit_mode'):
    show_edit_form()
elif action == "➕ Novo Produto":
    add_product_form()
else:
    manage_products_list_actions()
