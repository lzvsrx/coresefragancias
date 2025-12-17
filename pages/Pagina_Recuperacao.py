import streamlit as st
from utils.database import get_all_produtos, update_produto

st.title("🔄 Recuperação e Reposição")
st.markdown("Recupere produtos que foram zerados ou atualizados incorretamente.")

# Trazemos tudo para encontrar o que "sumiu"
todos = get_all_produtos(include_sold=True)

# Lista apenas os que estão com estoque 0
zerados = [p for p in todos if p.get("quantidade", 0) <= 0]

if not zerados:
    st.success("Tudo certo! Não há produtos 'sumidos' ou zerados.")
else:
    selecionado = st.selectbox("Selecione o produto para restaurar:", 
                                [p['nome'] for p in zerados])
    
    prod_data = next(p for p in zerados if p['nome'] == selecionado)
    
    with st.form("form_recuperar"):
        st.write(f"Restaurando: **{prod_data['nome']}**")
        nova_qtd = st.number_input("Nova Quantidade", min_value=1, value=1)
        novo_preco = st.number_input("Confirmar Preço", value=float(prod_data['preco']))
        
        if st.form_submit_button("Confirmar e Retornar ao Estoque"):
            update_produto(
                prod_data['id'], prod_data['nome'], novo_preco, nova_qtd,
                prod_data['marca'], prod_data['estilo'], prod_data['tipo'],
                prod_data['foto'], prod_data['data_validade']
            )
            st.success("Produto restaurado com sucesso!")
            st.rerun()
