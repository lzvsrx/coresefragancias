import streamlit as st
from utils.database import get_all_produtos, update_produto, MARCAS, ESTILOS, TIPOS

st.title("🔄 Recuperação e Reposição")
st.info("Aqui você encontra itens que saíram do estoque (qtd 0) e pode trazê-los de volta.")

# Puxa tudo e filtra apenas o que "sumiu" da visão de vendas
itens_zerados = [p for p in get_all_produtos(include_sold=True) if p['quantidade'] <= 0]

if not itens_zerados:
    st.success("Não há produtos zerados para recuperar!")
else:
    for p in itens_zerados:
        with st.expander(f"Repor: {p['nome']} (ID: {p['id']})"):
            with st.form(f"form_{p['id']}"):
                col1, col2 = st.columns(2)
                nova_qtd = col1.number_input("Nova Quantidade", min_value=1, value=1)
                novo_preco = col2.number_input("Preço Atual (R$)", value=float(p['preco']))
                
                if st.form_submit_button("Confirmar Reposição"):
                    update_produto(p['id'], p['nome'], novo_preco, nova_qtd, p['marca'], p['estilo'], p['tipo'], p['foto'], p['data_validade'])
                    st.success("Produto reativado com sucesso!")
                    st.rerun()
