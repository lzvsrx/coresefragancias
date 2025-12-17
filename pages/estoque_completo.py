import streamlit as st
from utils.database import get_all_produtos, ASSETS_DIR
import os

st.set_page_config(page_title="Estoque - Cores e Fragrâncias", layout="wide")

def format_to_brl(value):
    try:
        return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "R$ 0,00"

st.title("📦 Estoque Completo")

# include_sold=True garante que produtos com Qtd=0 apareçam aqui
produtos = get_all_produtos(include_sold=True)

if not produtos:
    st.info("Nenhum produto cadastrado.")
else:
    # Filtros SideBar para limpar a tela principal
    st.sidebar.header("Filtros")
    marcas = sorted(list({p['marca'] for p in produtos if p['marca']}))
    marca_f = st.sidebar.selectbox("Marca", ["Todas"] + marcas)
    
    # Lógica de Filtro
    prod_filtrados = [p for p in produtos if (marca_f == "Todas" or p['marca'] == marca_f)]

    st.subheader(f"Exibindo {len(prod_filtrados)} itens")
    
    for p in prod_filtrados:
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if p['foto'] and os.path.exists(os.path.join(ASSETS_DIR, p['foto'])):
                    st.image(os.path.join(ASSETS_DIR, p['foto']), width=150)
                else:
                    st.warning("Sem Foto")
            
            with col2:
                st.markdown(f"### {p['nome']}")
                st.write(f"**Marca:** {p['marca']} | **Estilo:** {p['estilo']}")
                qtd = p['quantidade']
                cor_texto = "red" if qtd <= 0 else "black"
                st.markdown(f"**Estoque:** :{cor_texto}[{qtd} unidades]")
                st.write(f"**Preço:** {format_to_brl(p['preco'])}")
                
                if qtd <= 0:
                    st.error("PRODUTO FORA DE ESTOQUE (VENDIDO)")
            st.divider()


