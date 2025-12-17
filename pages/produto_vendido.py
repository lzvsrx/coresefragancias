import streamlit as st
import os
from datetime import datetime
from utils.database import get_all_produtos, ASSETS_DIR

# --- Funções Auxiliares ---
def format_to_brl(value):
    """Formata um float para string no formato R$ 1.234.567,89."""
    try:
        num = float(value)
        formatted = f"{num:_.2f}".replace('.', ',').replace('_', '.')
        return "R$ " + formatted
    except (ValueError, TypeError):
        return "R$ N/A"

def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        try:
            with open(file_name, encoding='utf-8') as f: 
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except Exception:
            pass

# Configuração da página
# st.set_page_config(page_title="Produtos Vendidos - Cores e Fragrâncias") # Removido se já definido no main

load_css()

st.title("💰 Histórico de Itens Esgotados")
st.markdown("---")
st.info("Abaixo estão os produtos que foram marcados como vendidos e não possuem mais estoque físico (quantidade = 0).")

# 🔄 CHAMADA CRÍTICA: Corrigido para usar os argumentos aceitos pelo novo database.py
todos_produtos = get_all_produtos(include_out_of_stock=True) 

# Filtra produtos que estão com quantidade ZERO
# (A lógica assume que se está zero, ele foi 'vendido' até acabar)
produtos_esgotados = [p for p in todos_produtos if p.get("quantidade") == 0]

if not produtos_esgotados:
    st.info("Nenhum produto esgotado no momento. Todos os itens cadastrados possuem estoque.")
else:
    total_acumulado = 0.0
    
    # Criar colunas para métricas de resumo
    col_metrica1, col_metrica2 = st.columns(2)
    
    for p in produtos_esgotados:
        with st.container(border=True):
            col_info, col_img = st.columns([3, 1])
            
            try:
                preco_float = float(p.get('preco', 0))
                total_acumulado += preco_float
                
                with col_info:
                    st.subheader(f"✨ {p.get('nome')}")
                    st.write(f"**Preço Unitário:** {format_to_brl(preco_float)}")
                    st.write(f"**Marca:** {p.get('marca')} | **Tipo:** {p.get('tipo')}")
                    
                    # Se houver data de validade ou venda no seu banco:
                    validade = p.get('data_validade')
                    if validade:
                        st.caption(f"📅 Validade registrada: {validade}")

                with col_img:
                    if p.get("foto"):
                        photo_path = os.path.join(ASSETS_DIR, p.get('foto'))
                        if os.path.exists(photo_path):
                            st.image(photo_path, use_container_width=True)
                        else:
                            st.caption("🖼️ Sem foto")
                    else:
                        st.caption("🖼️ Sem foto")
            
            except Exception as e:
                st.error(f"Erro ao processar item: {e}")

    # Exibe o resumo financeiro no topo ou rodapé
    st.markdown("---")
    st.success(f"📊 **Valor Total Representado em Itens Esgotados:** {format_to_brl(total_acumulado)}")
