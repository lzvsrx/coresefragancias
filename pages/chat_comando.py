import streamlit as st
from utils.database import get_all_produtos, mark_produto_as_sold, get_produto_by_id

if not st.session_state.get("logged_in"): st.stop()

st.title("🤖 Chatbot de Vendas")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "Olá! Digite 'estoque' para ver itens ou 'vender' seguido do ID."}]

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ex: vender 12"):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    response = ""
    cmd = prompt.lower()
    
    if "estoque" in cmd:
        prods = get_all_produtos()
        response = "📋 **Itens:**\n" + "\n".join([f"- ID {p['id']}: {p['nome']} ({p['quantidade']} un)" for p in prods])
    elif "vender" in cmd:
        try:
            pid = int(cmd.split()[-1])
            p = get_produto_by_id(pid)
            if p and p['quantidade'] > 0:
                mark_produto_as_sold(pid, 1)
                response = f"✅ Venda de **{p['nome']}** realizada!"
            else: response = "❌ Produto indisponível ou ID inválido."
        except: response = "⚠️ Use: vender [ID]"
    else:
        response = "Dúvidas? Digite 'ajuda'."

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()
