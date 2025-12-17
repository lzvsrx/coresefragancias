import streamlit as st
import os
from datetime import datetime, date
from utils.database import (
    add_produto, get_all_produtos, mark_produto_as_sold,
    MARCAS, ESTILOS, TIPOS, get_produto_by_id
)

# --- Funções Auxiliares ---
def load_css(file_name="style.css"):
    """Carrega e aplica o CSS personalizado."""
    if os.path.exists(file_name):
        try:
            with open(file_name, encoding='utf-8') as f: 
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar CSS: {e}")

load_css()

# Configuração da página (Deve ser a primeira chamada Streamlit se for um script standalone)
# st.set_page_config(page_title="Chatbot de Estoque - Cores e Fragrâncias")

# --- Verificação de Segurança ---
if not st.session_state.get("logged_in"):
    st.error("🔒 **Acesso Negado.** Por favor, faça login na Área Administrativa.")
    st.info("O Chatbot operacional requer autenticação para realizar vendas e cadastros.")
    st.stop()

# --- ESTADO DO CHATBOT ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": f"Olá, **{st.session_state.get('username')}**! Sou seu assistente de estoque. Como posso ajudar? Digite `ajuda` para comandos."}
    ]
if "chat_state" not in st.session_state:
    st.session_state["chat_state"] = {"step": "idle", "data": {}}

st.title("🤖 Chatbot Operacional")
st.caption(f"Logado como: {st.session_state.get('username')} ({st.session_state.get('role')})")

def process_command(user_input: str):
    user_input = user_input.strip().lower()
    state = st.session_state["chat_state"]

    # --- Comando Global: Cancelar ---
    if user_input == "cancelar":
        st.session_state["chat_state"] = {"step": "idle", "data": {}}
        return "🛑 Operação cancelada. Como posso ajudar agora? (Dica: `ajuda` ou `estoque`)"

    # --- FLUXO: ADICIONAR PRODUTO (Máquina de Estados) ---
    if state["step"] == "add_waiting_nome":
        state["data"]["nome"] = user_input.title()
        state["step"] = "add_waiting_preco"
        return "Qual o **Preço**? (Ex: 59.90)"

    elif state["step"] == "add_waiting_preco":
        try:
            valor = float(user_input.replace(",", "."))
            if valor <= 0: return "O preço deve ser maior que zero."
            state["data"]["preco"] = valor
            state["step"] = "add_waiting_qtd"
            return "Qual a **Quantidade** inicial em estoque?"
        except ValueError: return "Por favor, digite um número válido para o preço."

    elif state["step"] == "add_waiting_qtd":
        try:
            qtd = int(user_input)
            if qtd < 0: return "A quantidade não pode ser negativa."
            state["data"]["quantidade"] = qtd
            state["step"] = "add_waiting_marca"
            return f"Escolha a **Marca**: {', '.join(MARCAS[:6])}..."
        except ValueError: return "Digite um número inteiro para a quantidade."

    elif state["step"] == "add_waiting_marca":
        match = [m for m in MARCAS if m.lower() == user_input]
        if match:
            state["data"]["marca"] = match[0]
            state["step"] = "add_waiting_validade"
            return "Qual a **Validade**? (DD/MM/AAAA ou 'nao')"
        return "Marca não encontrada. Verifique a grafia ou digite 'cancelar'."

    elif state["step"] == "add_waiting_validade":
        val_iso = None
        if user_input != 'nao':
            try:
                val_iso = datetime.strptime(user_input, "%d/%m/%Y").date().isoformat()
            except ValueError: return "Formato inválido. Use DD/MM/AAAA ou 'nao'."
        
        # Finalização do Cadastro
        try:
            add_produto(
                state["data"]["nome"], state["data"]["preco"], state["data"]["quantidade"],
                state["data"]["marca"], "Não Definido", "Geral", None, val_iso
            )
            nome_final = state["data"]["nome"]
            st.session_state["chat_state"] = {"step": "idle", "data": {}}
            return f"✅ **{nome_final}** cadastrado com sucesso!"
        except Exception as e:
            return f"❌ Erro ao salvar: {e}"

    # --- FLUXO: VENDER PRODUTO ---
    elif state["step"] == "sell_waiting_id":
        try:
            pid = int(user_input)
            p = get_produto_by_id(pid)
            if p:
                if p['quantidade'] > 0:
                    mark_produto_as_sold(pid, 1)
                    st.session_state["chat_state"] = {"step": "idle", "data": {}}
                    return f"💰 Venda registrada! **{p['nome']}** agora tem {p['quantidade'] - 1} un. no estoque."
                return "❌ Este produto está esgotado."
            return "ID não encontrado. Tente novamente ou 'cancelar'."
        except ValueError: return "Por favor, digite apenas o número do ID."

    # --- COMANDOS MODO 'IDLE' (ESPERA) ---
    if state["step"] == "idle":
        if user_input == "ajuda":
            return ("**Comandos que eu entendo:**\n"
                    "- `estoque`: Ver tudo o que temos.\n"
                    "- `vender`: Registrar uma saída.\n"
                    "- `adicionar`: Cadastrar novo item.\n"
                    "- `limpar`: Limpa a conversa.\n"
                    "- `cancelar`: Para o que estamos fazendo.")

        elif user_input == "estoque":
            prods = get_all_produtos()
            if not prods: return "Estoque vazio."
            msg = "**Itens disponíveis:**\n"
            for p in prods[:15]: # Limite para não poluir o chat
                msg += f"- `ID {p['id']}`: {p['nome']} | Qtd: **{p['quantidade']}** | R$ {p['preco']:.2f}\n"
            return msg

        elif user_input in ["vender", "venda"]:
            state["step"] = "sell_waiting_id"
            return "Certo! Digite o **ID do produto** vendido:"

        elif user_input in ["adicionar", "cadastrar"]:
            state["step"] = "add_waiting_nome"
            return "Vamos lá! Qual o **Nome** do produto?"

        elif user_input == "limpar":
            st.session_state["chat_history"] = []
            st.rerun()

    return "Não entendi. Digite `ajuda` para ver o que posso fazer."

# --- INTERFACE ---
for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite um comando (ex: 'vender' ou 'estoque')"):
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = process_command(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state["chat_history"].append({"role": "assistant", "content": response})
