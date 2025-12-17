
import streamlit as st
import os
from datetime import datetime, date
from typing import Dict, Any

# Protege import com fallback
try:
    from utils.database import (
        add_produto, get_all_produtos, mark_produto_as_sold, get_produto_by_id,
        MARCAS, ESTILOS, TIPOS
    )
except ImportError as e:
    st.error(f"❌ Erro no módulo database: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Erro crítico no database: {e}")
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Chatbot de Estoque - Cores e Fragrâncias", 
    page_icon="🤖",
    layout="wide"
)

# --- CARREGAMENTO DE CSS SEGURO ---
def load_css(file_name="style.css"):
    try:
        if os.path.exists(file_name):
            with open(file_name, encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception:
        pass  # Silencioso - não quebra a app

load_css()

# --- VERIFICAÇÃO DE LOGIN ---
if not st.session_state.get("logged_in", False):
    st.error("🔒 **Acesso Negado.** Faça login na Área Administrativa.")
    st.stop()

# --- INICIALIZAÇÃO SEGURA DE ESTADOS ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "Olá! Sou o assistente de estoque da **Cores e Fragrâncias**. Digite `ajuda` para ver comandos."}
    ]

if "chat_state" not in st.session_state:
    st.session_state["chat_state"] = {"step": "idle", "data": {}}

st.title("🤖 Chatbot Operacional")
st.caption("Gerencie seu estoque conversando comigo!")

# --- FUNÇÕES AUXILIARES SEGUROS ---
def safe_float(value: str) -> float:
    """Converte string para float com tratamento BRL."""
    try:
        return float(value.replace(",", ".").replace("R$", "").strip())
    except (ValueError, AttributeError):
        return 0.0

def safe_int(value: str) -> int:
    """Converte string para int seguro."""
    try:
        return int(value)
    except (ValueError, AttributeError):
        return 0

def safe_date(input_date: str) -> str:
    """Converte DD/MM/YYYY para ISO ou retorna None."""
    if input_date.lower() in ['nao', 'não', 'none', '']:
        return None
    try:
        return datetime.strptime(input_date, "%d/%m/%Y").date().isoformat()
    except ValueError:
        return None

def find_category(input_text: str, categories: list) -> str:
    """Encontra categoria exata ou fuzzy match."""
    input_text = input_text.strip().lower()
    for cat in categories:
        if input_text == cat.lower():
            return cat
    # Fuzzy match (primeiras 3 letras)
    for cat in categories:
        if input_text[:3] == cat.lower()[:3]:
            return cat
    return None

# --- LÓGICA DO CHATBOT (ROBUSTA) ---
def process_command(user_input: str) -> str:
    try:
        user_input = user_input.strip()
        if not user_input:
            return "🤔 Digite algo para eu ajudar! (`ajuda`)"
            
        state = st.session_state["chat_state"]
        user_input_lower = user_input.lower()

        # CANCELAR QUALQUER FLUXO
        if user_input_lower == "cancelar":
            st.session_state["chat_state"] = {"step": "idle", "data": {}}
            return "🛑 Operação cancelada. Como posso ajudar? (`ajuda`)"

        # FLUXO ADICIONAR PRODUTO
        if state["step"] == "add_waiting_nome":
            state["data"]["nome"] = user_input.title().strip()
            if not state["data"]["nome"]:
                return "❌ Nome inválido. Digite novamente:"
            state["step"] = "add_waiting_preco"
            return f"✅ Nome: **{state['data']['nome']}**. Agora o **Preço**? (Ex: 59,90)"

        elif state["step"] == "add_waiting_preco":
            preco = safe_float(user_input)
            if preco <= 0:
                return "❌ Preço deve ser > 0. Ex: `59.90` ou `45,00`:"
            state["data"]["preco"] = preco
            state["step"] = "add_waiting_qtd"
            return f"✅ Preço: **R$ {preco:.2f}**. **Quantidade** inicial?"

        elif state["step"] == "add_waiting_qtd":
            qtd = safe_int(user_input)
            if qtd < 0:
                return "❌ Quantidade não pode ser negativa:"
            state["data"]["quantidade"] = qtd
            state["step"] = "add_waiting_marca"
            return f"✅ Qtd: **{qtd} un**. Escolha a **Marca**:\n{', '.join(MARCAS[:5])}..."

        elif state["step"] == "add_waiting_marca":
            marca = find_category(user_input, MARCAS)
            if marca:
                state["data"]["marca"] = marca
                state["step"] = "add_waiting_estilo"
                return f"✅ Marca: **{marca}**. Agora **Estilo**? (Perfumaria, Skincare...)"
            return f"❌ Marca inválida. Escolha: {', '.join(MARCAS[:5])}... ou `cancelar`"

        elif state["step"] == "add_waiting_estilo":
            estilo = find_category(user_input, ESTILOS)
            if estilo:
                state["data"]["estilo"] = estilo
                state["step"] = "add_waiting_tipo"
                return f"✅ Estilo: **{estilo}**. **Tipo específico**?"
            return "❌ Estilo inválido. Tente: Perfumaria, Skincare... ou `cancelar`"

        elif state["step"] == "add_waiting_tipo":
            tipo = find_category(user_input, TIPOS)
            if tipo:
                state["data"]["tipo"] = tipo
                state["step"] = "add_waiting_validade"
                return "✅ Tipo ok! **Validade** (DD/MM/AAAA) ou `não`:"
            return "❌ Tipo inválido. Tente outro ou `cancelar`"

        elif state["step"] == "add_waiting_validade":
            data_validade = safe_date(user_input)
            try:
                new_id = add_produto(
                    state["data"]["nome"],
                    state["data"]["preco"],
                    state["data"]["quantidade"],
                    state["data"]["marca"],
                    state["data"]["estilo"],
                    state["data"]["tipo"],
                    None,  # foto
                    data_validade
                )
                nome_final = state["data"]["nome"]
                st.session_state["chat_state"] = {"step": "idle", "data": {}}
                return f"🎉 **{nome_final}** adicionado! ID: **{new_id}**"
            except Exception as e:
                return f"❌ Erro ao salvar: {str(e)[:100]}"

        # FLUXO VENDA
        elif state["step"] == "sell_waiting_id":
            pid = safe_int(user_input)
            if pid <= 0:
                return "❌ ID inválido. Digite apenas o número:"
            try:
                mark_produto_as_sold(pid, 1)
                st.session_state["chat_state"] = {"step": "idle", "data": {}}
                return f"💰 Venda ID **{pid}** registrada! Estoque atualizado."
            except ValueError as e:
                return f"❌ {str(e)}"
            except Exception:
                return "❌ Erro na venda. Verifique o ID e estoque."

        # ESTADO INICIAL (IDLE)
        if state["step"] == "idle":
            if "ajuda" in user_input_lower:
                return """✨ **COMANDOS DISPONÍVEIS:**
• `adicionar produto` - Cadastra novo item
• `estoque` ou `estoque [marca]` - Lista itens
• `vender` ou `vender [ID]` - Registra venda
• `cancelar` - Para qualquer operação"""

            elif "adicionar produto" in user_input_lower:
                st.session_state["chat_state"]["step"] = "add_waiting_nome"
                return "🚀 **NOVO PRODUTO** - Qual o **nome**?"

            elif user_input_lower.startswith("vender"):
                parts = user_input.split()
                if len(parts) > 1 and parts[1].isdigit():
                    return process_command(parts[1])  # Processa ID direto
                st.session_state["chat_state"]["step"] = "sell_waiting_id"
                return "💰 **VENDA** - Digite o **ID** do produto:"

            elif "estoque" in user_input_lower:
                try:
                    produtos = get_all_produtos(include_sold=False)
                    if not produtos:
                        return "📦 Estoque vazio no momento."

                    # Filtro por marca
                    marca_filtro = None
                    parts = user_input_lower.split("estoque ")
                    if len(parts) > 1:
                        marca_filtro = parts[1].strip()
                        produtos = [p for p in produtos if p.get('marca', '').lower() == marca_filtro.lower()]
                    
                    if not produtos:
                        return f"📦 Nenhum item {'da marca ' + marca_filtro if marca_filtro else ''}em estoque."

                    resp = f"📦 **ESTOQUE** ({len(produtos)} itens):\n\n"
                    for p in produtos[:10]:  # Limite seguro
                        nome = p.get('nome', 'N/A')[:30]
                        qtd = p.get('quantidade', 0)
                        preco = p.get('preco', 0)
                        resp += f"• **ID {p.get('id', '?')}** {nome} | {qtd}un | R${preco:.2f}\n"
                    
                    if len(produtos) > 10:
                        resp += f"\n...e mais {len(produtos)-10} itens."
                    return resp

                except Exception:
                    return "❌ Erro ao consultar estoque."

        return "🤔 Não entendi. Digite `ajuda` para comandos."

    except Exception as e:
        return f"⚠️ Erro interno: {str(e)[:50]} (`ajuda` para continuar)"

# --- INTERFACE DE CHAT ---
st.markdown("---")

# Histórico
for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input
if prompt := st.chat_input("Digite um comando (ex: 'adicionar produto', 'estoque', 'ajuda')..."):
    # Adiciona mensagem do user
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Processa resposta
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            resposta = process_command(prompt)
            st.markdown(resposta)
    
    # Salva na história
    st.session_state["chat_history"].append({"role": "assistant", "content": resposta})
    
    # Limpa histórico se muito grande
    if len(st.session_state["chat_history"]) > 50:
        st.session_state["chat_history"] = st.session_state["chat_history"][-40:]
    
    # Rerun apenas em ações críticas
    if any(x in resposta.lower() for x in ["sucesso", "vendida", "adicionado"]):
        st.rerun()

