import streamlit as st
import os
from datetime import datetime
from utils.database import get_all_produtos, ASSETS_DIR

# --- Funções Auxiliares ---

def format_to_brl(value):
    """Formata um float para string no formato R$ 1.234.567,89."""
    try:
        num = float(value)
        # Formata com separador de milhar e decimal brasileiro
        formatted = f"{num:_.2f}".replace('.', ',').replace('_', '.')
        return "R$ " + formatted
    except (ValueError, TypeError):
        return "R$ N/A"

def load_css(file_name="style.css"):
    """Carrega o CSS garantindo suporte a caracteres especiais."""
    if os.path.exists(file_name):
        try:
            with open(file_name, encoding='utf-8') as f: 
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar CSS: {e}")

# --- Configuração da Página ---

# st.set_page_config deve ser a primeira chamada Streamlit se este arquivo for executado sozinho
# Se for parte de um multipage app, o config do main.py costuma prevalecer.
load_css("style.css")

st.title("📦 Estoque Completo")
st.markdown("---")

# 🔄 CHAMADA CORRIGIDA: Compatível com a nova definição no database.py
# Usamos include_out_of_stock=True para que o usuário possa ver tudo, inclusive o que acabou
produtos = get_all_produtos(include_out_of_stock=True)

if not produtos:
    st.info("Nenhum produto cadastrado no estoque.")
else:
    # --- Seção de Filtros ---
    with st.expander("🔍 Filtros de Busca", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        # Coleta de categorias únicas de forma segura
        marcas = sorted(list({p.get("marca") for p in produtos if p.get("marca")}))
        estilos = sorted(list({p.get("estilo") for p in produtos if p.get("estilo")}))
        tipos = sorted(list({p.get("tipo") for p in produtos if p.get("tipo")}))

        with col1:
            marca_filtro = st.selectbox("Marca", ["Todas"] + marcas)
        with col2:
            estilo_filtro = st.selectbox("Estilo", ["Todos"] + estilos)
        with col3:
            tipo_filtro = st.selectbox("Tipo", ["Todos"] + tipos)

    # Aplicação da lógica de filtros
    produtos_exibicao = produtos
    if marca_filtro != "Todas":
        produtos_exibicao = [p for p in produtos_exibicao if p.get("marca") == marca_filtro]
    if estilo_filtro != "Todos": 
        produtos_exibicao = [p for p in produtos_exibicao if p.get("estilo") == estilo_filtro]
    if tipo_filtro != "Todos":
        produtos_exibicao = [p for p in produtos_exibicao if p.get("tipo") == tipo_filtro]

    st.subheader(f"📊 {len(produtos_exibicao)} produtos listados")
    
    total_estoque_valor = 0.0

    # --- Listagem de Produtos ---
    for p in produtos_exibicao:
        with st.container(border=True):
            col_txt, col_img = st.columns([3, 1])
            
            try:
                preco_float = float(p.get('preco', 0))
                qtd_int = int(p.get('quantidade', 0))
                valor_total_item = preco_float * qtd_int
                total_estoque_valor += valor_total_item
                
                with col_txt:
                    st.markdown(f"### **{p.get('nome')}**")
                    st.write(f"**Marca:** {p.get('marca')} | **Estilo:** {p.get('estilo')} | **Tipo:** {p.get('tipo')}")
                    
                    # Alerta visual para estoque zerado
                    if qtd_int == 0:
                        st.error(f"⚠️ **ESTOQUE ZERADO**")
                    else:
                        st.write(f"**Quantidade:** {qtd_int} un.")
                    
                    st.write(f"**Preço Unitário:** {format_to_brl(preco_float)}")
                    st.write(f"**Subtotal em Estoque:** {format_to_brl(valor_total_item)}")
                    
                    validade = p.get('data_validade')
                    st.caption(f"📅 Validade: {validade if validade else 'Não informada'}")

                with col_img:
                    if p.get("foto"):
                        path = os.path.join(ASSETS_DIR, p.get('foto'))
                        if os.path.exists(path):
                            st.image(path, use_container_width=True)
                        else:
                            st.caption("🖼️ Sem foto")
                    else:
                        st.caption("🖼️ Sem foto")

            except Exception as e:
                st.error(f"Erro ao exibir item ID {p.get('id')}: {e}")

    # --- Resumo Financeiro ---
    st.markdown("---")
    st.success(f"💰 **Valor Total do Estoque Exibido:** {format_to_brl(total_estoque_valor)}")
