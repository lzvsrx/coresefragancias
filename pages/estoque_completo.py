import streamlit as st
from utils.database import get_all_produtos, ASSETS_DIR
import os

st.set_page_config(page_title="Estoque Completo", layout="wide")

def format_to_brl(value):
    try:
        return f"R$ {float(value):_.2f}".replace('.', ',').replace('_', '.')
    except: return "R$ 0,00"

st.title("📦 Controle de Estoque")

# 🔄 Pega TUDO (incluindo os que "sumiram" por estar com qtd 0)
produtos = get_all_produtos(include_sold=True)

if not produtos:
    st.info("Nenhum produto no sistema.")
else:
    # Filtros
    col1, col2, col3 = st.columns(3)
    marcas = sorted(list({p['marca'] for p in produtos if p['marca']}))
    with col1:
        f_marca = st.selectbox("Marca", ["Todas"] + marcas)
    
    # Aplicação do Filtro
    filtrados = [p for p in produtos if (f_marca == "Todas" or p['marca'] == f_marca)]

    st.write(f"Exibindo {len(filtrados)} produtos.")

    for p in filtrados:
        with st.container():
            c1, c2, c3 = st.columns([1, 3, 1])
            
            with c1:
                path = os.path.join(ASSETS_DIR, p['foto']) if p['foto'] else ""
                if path and os.path.exists(path):
                    st.image(path, width=120)
                else:
                    st.write("🖼️ Sem Foto")
            
            with c2:
                st.subheader(p['nome'])
                st.write(f"**Preço:** {format_to_brl(p['preco'])} | **Validade:** {p['data_validade']}")
                
                # Alerta visual para produtos zerados
                if p['quantidade'] <= 0:
                    st.error(f"⚠️ ESTOQUE ZERADO (Vendido)")
                else:
                    st.success(f"✅ Disponível: {p['quantidade']} unidades")
            
            with c3:
                # Botão para "Recuperar" ou Editar rapidamente
                if st.button("📝 Editar/Repor", key=f"ed_{p['id']}"):
                    st.session_state['editar_id'] = p['id']
                    st.info("Vá para a página de Cadastro/Edição para alterar.")
        st.divider()
