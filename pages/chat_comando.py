import streamlit as st
import os
from datetime import datetime, date
from utils.database import (
    add_produto, get_all_produtos, mark_produto_as_sold,
    MARCAS, ESTILOS, TIPOS
)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chatbot de Estoque - Cores e Fragrâncias", page_icon="🤖")

# --- CARREGAMENTO DE CSS ---
def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        try:
            with open(file_name, encoding='utf-8') as f: 
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar CSS: {e}")

load_css()

# --- VERIFICAÇÃO DE LOGIN ---
if not st.session_state.get("logged_in"):
    st.error("🔒 **Acesso Negado.** Por favor, faça login na Área Administrativa para usar o assistente.")
    st.info("Vá para a página inicial ou Área Administrativa.")
    st.stop()

# --- INICIALIZAÇÃO DE ESTADOS ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "Olá! Sou o assistente de estoque da **Cores e Fragrâncias**. Como posso ajudar? Digite `ajuda` para ver os comandos."}
    ]
if "chat_state" not in st.session_state:
    st.session_state["chat_state"] = {"step": "idle", "data": {}}

st.title("🤖 Chatbot Operacional")
st.caption("Gerencie seu estoque conversando com o sistema.")

# --- LÓGICA DO CHATBOT ---
def process_command(user_input: str):
    user_input = user_input.strip().lower()
    state = st.session_state["chat_state"]
    
    # Comandos Globais
    if user_input == "cancelar":
        st.session_state["chat_state"] = {"step": "idle", "data": {}}
        return "🛑 Operação cancelada. Como posso ajudar agora? (Digite `ajuda`)"

    # --- FLUXO: ADICIONAR PRODUTO ---
    if state["step"] == "add_waiting_nome":
        state["data"]["nome"] = user_input.title()
        state["step"] = "add_waiting_preco"
        return f"Nome definido como **{state['data']['nome']}**. Agora, qual o **Preço**? (Ex: 59.90)"
    
    elif state["step"] == "add_waiting_preco":
        try:
            preco = float(user_input.replace(",", "."))
            if preco <= 0: return "O preço deve ser maior que zero. Tente novamente."
            state["data"]["preco"] = preco
            state["step"] = "add_waiting_qtd"
            return "Perfeito. Qual a **Quantidade** inicial em estoque?"
        except ValueError: return "Preço inválido. Digite um número (Ex: 45.00)."
            
    elif state["step"] == "add_waiting_qtd":
        try:
            qtd = int(user_input)
            if qtd < 0: return "A quantidade não pode ser negativa."
            state["data"]["quantidade"] = qtd
            state["step"] = "add_waiting_marca"
            return f"Qual a **Marca**? Sugestões: {', '.join(MARCAS[:4])}."
        except ValueError: return "Por favor, digite um número inteiro para a quantidade."
    
    elif state["step"] == "add_waiting_marca":
        marca_encontrada = next((m for m in MARCAS if m.lower() == user_input), None)
        if marca_encontrada:
            state["data"]["marca"] = marca_encontrada
            state["step"] = "add_waiting_estilo"
            return f"Marca **{marca_encontrada}** selecionada. Qual o **Estilo**? (Ex: Perfumaria, Skincare...)"
        return "Marca não cadastrada. Por favor, escolha uma marca válida ou digite `cancelar`."

    elif state["step"] == "add_waiting_estilo":
        estilo_encontrado = next((e for e in ESTILOS if e.lower() == user_input), None)
        if estilo_encontrado:
            state["data"]["estilo"] = estilo_encontrado
            state["step"] = "add_waiting_tipo"
            return f"Estilo **{estilo_encontrado}** ok. Qual o **Tipo** específico?"
        return "Estilo não reconhecido. Tente novamente."

    elif state["step"] == "add_waiting_tipo":
        tipo_encontrado = next((t for t in TIPOS if t.lower() == user_input), None)
        if tipo_encontrado:
            state["data"]["tipo"] = tipo_encontrado
            state["step"] = "add_waiting_validade"
            return "Último passo: Qual a **Validade**? (DD/MM/AAAA) ou digite `nao`."
        return "Tipo não encontrado na lista oficial. Tente outro."

    elif state["step"] == "add_waiting_validade":
        val_iso = None
        if user_input != 'nao':
            try:
                val_iso = datetime.strptime(user_input, "%d/%m/%Y").date().isoformat()
            except ValueError: return "Data inválida. Use o formato DD/MM/AAAA ou digite `nao`."
        
        try:
            add_produto(state["data"]["nome"], state["data"]["preco"], state["data"]["quantidade"], 
                        state["data"]["marca"], state["data"]["estilo"], state["data"]["tipo"], None, val_iso)
            nome_final = state["data"]["nome"]
            st.session_state["chat_state"] = {"step": "idle", "data": {}}
            return f"✅ Sucesso! O produto **{nome_final}** foi adicionado ao estoque."
        except Exception as e:
            return f"❌ Erro ao salvar no banco: {e}"

    # --- FLUXO: VENDER PRODUTO ---
    elif state["step"] == "sell_waiting_id":
        try:
            pid = int(user_input)
            mark_produto_as_sold(pid, 1)
            st.session_state["chat_state"] = {"step": "idle", "data": {}}
            return f"💰 Venda registrada com sucesso para o ID **{pid}**! Estoque atualizado."
        except ValueError as e: return f"❌ Erro: {e}. Verifique o ID e o estoque disponível."
        except Exception: return "ID inválido. Digite apenas o número ou `cancelar`."

    # --- ESTADO IDLE (AGUARDANDO COMANDOS) ---
    if state["step"] == "idle":
        if "ajuda" in user_input:
            return ("✨ **Comandos que eu entendo:**\n\n"
                    "1. `adicionar produto` - Cadastro guiado passo a passo.\n"
                    "2. `estoque` - Lista todos os itens disponíveis.\n"
                    "3. `vender [ID]` - Registra a venda de 1 unidade.\n"
                    "4. `vender` - Eu pergunto qual o ID do item.\n"
                    "5. `cancelar` - Interrompe qualquer ação atual.")

        elif "adicionar produto" in user_input:
            state["step"] = "add_waiting_nome"
            return "Vamos lá! Qual o **Nome** do novo produto?"

        elif user_input.startswith("vender"):
            parts = user_input.split()
            if len(parts) > 1:
                return process_command(parts[1]) # Tenta processar o ID direto
            state["step"] = "sell_waiting_id"
            return "Certo. Digite o **ID** do produto vendido:"

        elif "estoque" in user_input:
            produtos = get_all_produtos(include_out_of_stock=False)
            if not produtos: return "O estoque está vazio no momento."
            
            # Filtro por marca se o comando for 'estoque boticário'
            parts = user_input.split("estoque ")
            if len(parts) > 1:
                marca_filtro = parts[1].strip()
                produtos = [p for p in produtos if p['marca'].lower() == marca_filtro]
                if not produtos: return f"Nenhum item da marca **{marca_filtro}** em estoque."

            resp = "**📋 Itens em Estoque:**\n"
            for p in produtos[:15]: # Limita a 15 para não poluir o chat
                resp += f"- ID `{p['id']}`: **{p['nome']}** | {p['quantidade']} un | R$ {p['preco']:.2f}\n"
            if len(produtos) > 15: resp += "\n*...e mais itens. Veja a página de Estoque Completo para a lista total.*"
            return resp

    return "🤔 Não entendi. Digite `ajuda` para ver o que posso fazer."

# --- INTERFACE DE CHAT ---
for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite um comando (ex: 'adicionar produto' ou 'ajuda')..."):
    # Mostra mensagem do usuário
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Processa e mostra resposta
    resposta = process_command(prompt)
    with st.chat_message("assistant"):
        st.markdown(resposta)
    st.session_state["chat_history"].append({"role": "assistant", "content": resposta})
    
    # Rerun para atualizar métricas se necessário (apenas em ações de alteração)
    if "Sucesso" in resposta or "registrada" in resposta:
        st.rerun()
