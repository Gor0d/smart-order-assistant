from google import genai
from google.genai import types
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class CustomerSupportAgent:
    def __init__(self):
        # Tenta pegar do Streamlit secrets primeiro, depois do .env
        try:
            import streamlit as st
            api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv('GOOGLE_API_KEY'))
        except:
            api_key = os.getenv('GOOGLE_API_KEY')

        if not api_key:
            raise ValueError("❌ GOOGLE_API_KEY não encontrada! Configure no arquivo .env ou Streamlit secrets")

        self.client = genai.Client(api_key=api_key)

        self.system_prompt = """
        Você é um assistente de atendimento do iFood, uma plataforma de delivery.

        REGRAS:
        - Seja empático e profissional
        - Resolva o problema do cliente de forma clara
        - Se for atraso: informe que está verificando e dê previsão
        - Se for cancelamento: pergunte o motivo e processe
        - Se for produto errado: ofereça reembolso ou reenvio
        - Sempre finalize perguntando se há mais algo

        Responda em português, de forma direta e amigável.
        """

    def atender(self, mensagem_cliente):
        """Processa mensagem do cliente e retorna resposta"""

        prompt = f"""
        {self.system_prompt}

        CLIENTE: {mensagem_cliente}

        ASSISTENTE:
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Erro ao processar: {str(e)}"

    def classificar_intencao(self, mensagem):
        """Classifica a intenção da mensagem"""

        prompt = f"""
        Classifique a intenção desta mensagem em UMA categoria:
        - atraso
        - produto
        - cancelamento
        - pagamento
        - duvida

        Mensagem: {mensagem}

        Responda APENAS com o nome da categoria, nada mais.
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            return response.text.strip().lower()
        except Exception as e:
            return f"erro: {str(e)}"


# Teste
if __name__ == "__main__":
    print("🚀 Iniciando teste do agente...")

    try:
        agent = CustomerSupportAgent()
        print("✅ Agente inicializado com sucesso!\n")

        # Teste 1
        print("=" * 60)
        print("📝 TESTE 1: Atendimento")
        print("=" * 60)
        mensagem1 = "Meu pedido está atrasado há 1 hora!"
        print(f"Cliente: {mensagem1}")
        resposta = agent.atender(mensagem1)
        print(f"\n🤖 Assistente:\n{resposta}\n")

        # Teste 2
        print("=" * 60)
        print("📝 TESTE 2: Classificação de Intenção")
        print("=" * 60)
        mensagem2 = "Quero cancelar meu pedido"
        print(f"Cliente: {mensagem2}")
        intencao = agent.classificar_intencao(mensagem2)
        print(f"🎯 Intenção detectada: {intencao}\n")

        # Teste 3
        print("=" * 60)
        print("📝 TESTE 3: Produto errado")
        print("=" * 60)
        mensagem3 = "Veio hambúrguer mas pedi pizza"
        print(f"Cliente: {mensagem3}")
        resposta3 = agent.atender(mensagem3)
        print(f"\n🤖 Assistente:\n{resposta3}\n")

        print("=" * 60)
        print("✅ Todos os testes concluídos!")
        print("=" * 60)

    except ValueError as e:
        print(f"\n❌ ERRO: {e}")
        print("\n💡 SOLUÇÃO:")
        print("1. Pegue sua API key em: https://aistudio.google.com/app/apikey")
        print("2. Crie um arquivo .env na raiz do projeto")
        print("3. Adicione: GOOGLE_API_KEY=sua_chave_aqui")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")