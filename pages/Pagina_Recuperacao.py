import streamlit as st
from utils.database import get_all_produtos, update_produto

st.title("🔄 Recuperação de Itens Sumidos")
st.markdown("Itens com quantidade 0 que saíram do estoque principal aparecem aqui para reposição.")

# Busca direta no banco por itens zerados
itens_sumidos = [p for p in get_all_produtos(include_sold=True) if p['quantidade'] <= 0]

if not itens_sumidos:
    st.success("Não há produtos para recuperar (estoque está positivo em tudo).")
else:
    for p in itens_sumidos:
        with st.expander(f"Recuperar: {p['nome']} (ID {p['id']})"):
            st.warning(f"Dados atuais: Marca {p['marca']} | Preço anterior {p['preco']}")
            with st.form(f"f_rec_{p['id']}"):
                c1, c2 = st.columns(2)
                nova_qtd = c1.number_input("Quantidade para Repor", min_value=1, value=10)
                novo_preco = c2.number_input("Ajustar Preço (R$)", value=float(p['preco']))
                
                if st.form_submit_button("Confirmar Reposição e Salvar no Banco"):
                    update_produto(p['id'], p['nome'], novo_preco, nova_qtd, p['marca'], p['estilo'], p['tipo'], p['foto'], p['data_validade'])
                    st.success(f"O item '{p['nome']}' foi devolvido ao estoque!")
                    st.rerun()
