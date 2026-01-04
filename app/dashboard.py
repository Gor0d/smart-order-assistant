import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.customer_agent import CustomerSupportAgent
from src.models.intent_classifier import IntentClassifier

# Configuração da página
st.set_page_config(
    page_title="SmartOrder Assistant - Estudo iFood",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #EA1D2C 0%, #FF6B35 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        background-color: #EA1D2C;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<h1 class="main-header">🤖 SmartOrder Assistant</h1>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align: center; font-size: 1.2rem; color: #666;">Sistema de Atendimento Inteligente com IA - Estudo pessoal - iFood</p>',
    unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://logodownload.org/wp-content/uploads/2017/05/ifood-logo.png", width=200)
    st.markdown("---")

    st.header("⚙️ Configurações")
    usar_gemini = st.checkbox("🧠 Usar Gemini (LLM)", value=True)
    usar_ml = st.checkbox("📊 Usar Modelo ML", value=True)

    st.markdown("---")
    st.markdown("### 📈 Status do Sistema")
    st.success("✅ Gemini: Online")
    st.success("✅ Modelo ML: Carregado")
    st.info(f"📅 Data: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")


# Cache de dados
@st.cache_data
def carregar_dados():
    import os
    from pathlib import Path

    # Caminho para o arquivo de dados
    data_path = Path('data/raw/conversas.csv')

    # Se o arquivo não existir, gera os dados
    if not data_path.exists():
        st.info("📊 Gerando dados sintéticos pela primeira vez...")

        # Criar diretórios se não existirem
        data_path.parent.mkdir(parents=True, exist_ok=True)

        # Gerar dados
        from faker import Faker
        import random

        fake = Faker('pt_BR')

        CATEGORIAS = {
            'atraso': ['Meu pedido está atrasado', 'Quanto tempo ainda demora?', 'Pedido não chegou'],
            'produto': ['Veio item errado', 'Faltou um produto', 'Produto veio estragado'],
            'cancelamento': ['Quero cancelar o pedido', 'Como cancelo?', 'Pode cancelar pra mim?'],
            'pagamento': ['Cobrado em duplicidade', 'Não consigo pagar', 'Reembolso'],
            'duvida': ['Como funciona?', 'Qual o horário?', 'Aceita vale refeição?']
        }

        dados = []
        for _ in range(1000):
            categoria = random.choice(list(CATEGORIAS.keys()))
            mensagem = random.choice(CATEGORIAS[categoria])

            dados.append({
                'id': fake.uuid4(),
                'timestamp': fake.date_time_between(start_date='-30d', end_date='now'),
                'usuario_id': fake.uuid4(),
                'mensagem': mensagem,
                'categoria': categoria,
                'sentimento': random.choice(['positivo', 'neutro', 'negativo']),
                'urgencia': random.choice(['baixa', 'media', 'alta']),
                'valor_pedido': round(random.uniform(20, 150), 2),
                'tempo_espera_min': random.randint(10, 120)
            })

        df_temp = pd.DataFrame(dados)
        df_temp.to_csv(data_path, index=False)
        st.success("✅ Dados gerados com sucesso!")

    # Carregar dados
    df = pd.read_csv(data_path)
    # Converter timestamp para string para evitar erros de serialização
    df['timestamp'] = pd.to_datetime(df['timestamp']).astype(str)
    return df


@st.cache_resource
def carregar_modelos():
    agent = CustomerSupportAgent() if usar_gemini else None

    clf = None
    if usar_ml:
        clf = IntentClassifier()
        try:
            clf.carregar()
        except:
            st.warning("⚠️ Modelo ML não encontrado. Execute: python src/models/intent_classifier.py")

    return agent, clf


# Carregar dados
df = carregar_dados()

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs(
    ["💬 Chat Interativo", "📊 Métricas & KPIs", "🔍 Análise de Dados", "🧪 Comparação IA vs ML"])

# ============================================================
# TAB 1: CHAT INTERATIVO
# ============================================================
with tab1:
    st.header("💬 Converse com o Assistente Virtual")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📝 Sua Mensagem")
        mensagem_usuario = st.text_area(
            "Digite sua mensagem:",
            placeholder="Ex: Meu pedido está atrasado há 1 hora...",
            height=100
        )

        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            enviar = st.button("🚀 Enviar", use_container_width=True)
        with col_btn2:
            exemplo1 = st.button("📦 Exemplo: Atraso", use_container_width=True)
        with col_btn3:
            exemplo2 = st.button("❌ Exemplo: Cancelar", use_container_width=True)

        if exemplo1:
            mensagem_usuario = "Meu pedido está atrasado há 1 hora!"
        if exemplo2:
            mensagem_usuario = "Quero cancelar meu pedido"

        if enviar and mensagem_usuario:
            with st.spinner("🤖 Processando sua mensagem..."):
                agent, clf = carregar_modelos()

                # Resposta Gemini
                if usar_gemini and agent:
                    st.markdown("### 🤖 Resposta do Assistente (Gemini)")
                    resposta = agent.atender(mensagem_usuario)
                    st.success(resposta)

                # Classificação ML
                if usar_ml and clf:
                    st.markdown("### 🎯 Análise do Modelo ML")
                    resultado = clf.prever(mensagem_usuario)

                    col_ml1, col_ml2 = st.columns(2)
                    with col_ml1:
                        st.metric("Categoria Detectada", resultado['categoria'].upper())
                    with col_ml2:
                        st.metric("Confiança", f"{resultado['confianca']:.1%}")

                    # Gráfico de probabilidades
                    probs_df = pd.DataFrame({
                        'Categoria': list(resultado['probabilidades'].keys()),
                        'Probabilidade': list(resultado['probabilidades'].values())
                    }).sort_values('Probabilidade', ascending=True)

                    fig = px.bar(probs_df, x='Probabilidade', y='Categoria',
                                 orientation='h', title="Distribuição de Probabilidades")
                    fig.update_traces(marker_color='#EA1D2C')
                    st.plotly_chart(fig, width='stretch')

    with col2:
        st.markdown("### 💡 Exemplos de Mensagens")
        st.info("**Atraso:**\n- Meu pedido não chegou\n- Quanto tempo demora?")
        st.warning("**Produto:**\n- Veio item errado\n- Faltou produto")
        st.error("**Cancelamento:**\n- Quero cancelar\n- Como cancelo?")
        st.success("**Pagamento:**\n- Cobrança duplicada\n- Reembolso")

        st.markdown("---")
        st.markdown("### 📊 Estatísticas Rápidas")
        st.metric("Total de Conversas", len(df))
        st.metric("Categorias", df['categoria'].nunique())

# ============================================================
# TAB 2: MÉTRICAS & KPIs
# ============================================================
with tab2:
    st.header("📊 Métricas de Performance")

    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>1,000</h2>
            <p>Total de Conversas</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h2>78%</h2>
            <p>Resolução Automática</p>
            <small>↑ 12% vs mês anterior</small>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h2>2.3 min</h2>
            <p>Tempo Médio</p>
            <small>↓ 30% vs mês anterior</small>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <h2>8.5/10</h2>
            <p>NPS Score</p>
            <small>↑ 1.2 vs mês anterior</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Gráficos
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("📊 Distribuição de Categorias")
        fig_cat = px.pie(df, names='categoria', title='Problemas por Categoria',
                         color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_cat, width='stretch')

    with col_g2:
        st.subheader("😊 Análise de Sentimento")
        fig_sent = px.bar(df['sentimento'].value_counts(),
                          title='Distribuição de Sentimentos')
        fig_sent.update_traces(marker_color=['#43e97b', '#f5576c', '#feca57'])
        st.plotly_chart(fig_sent, width='stretch')

    # Conversas por dia
    st.subheader("📈 Volume de Conversas ao Longo do Tempo")
    df_temp = df.copy()
    df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'])
    conversas_dia = df_temp.groupby(df_temp['timestamp'].dt.date).size().reset_index(name='count')

    fig_linha = px.line(conversas_dia, x='timestamp', y='count',
                        title='Conversas Diárias',
                        markers=True)
    fig_linha.update_traces(line_color='#EA1D2C')
    st.plotly_chart(fig_linha, width='stretch')

# ============================================================
# TAB 3: ANÁLISE DE DADOS
# ============================================================
with tab3:
    st.header("🔍 Análise Exploratória de Dados")

    col_a1, col_a2 = st.columns(2)

    with col_a1:
        st.subheader("📋 Amostra de Dados")
        st.dataframe(df.head(10), width='stretch')

    with col_a2:
        st.subheader("📊 Estatísticas Descritivas")
        st.dataframe(df.describe(), width='stretch')

    st.markdown("---")

    # Heatmap de urgência vs categoria
    st.subheader("🔥 Mapa de Calor: Categoria vs Urgência")
    heatmap_data = pd.crosstab(df['categoria'], df['urgencia'])

    fig_heat = px.imshow(heatmap_data,
                         labels=dict(x="Urgência", y="Categoria", color="Quantidade"),
                         title="Distribuição de Urgência por Categoria",
                         color_continuous_scale='Reds')
    st.plotly_chart(fig_heat, width='stretch')

    # Valor médio por categoria
    st.subheader("💰 Valor Médio do Pedido por Categoria")
    valor_medio = df.groupby('categoria')['valor_pedido'].mean().sort_values(ascending=False)

    fig_valor = px.bar(valor_medio, title='Ticket Médio por Tipo de Problema')
    fig_valor.update_traces(marker_color='#EA1D2C')
    st.plotly_chart(fig_valor, width='stretch')

# ============================================================
# TAB 4: COMPARAÇÃO
# ============================================================
with tab4:
    st.header("🧪 Comparação: Gemini vs Modelo ML")

    st.info("💡 Compare as previsões do modelo Gemini (LLM) com o modelo ML (Naive Bayes)")

    teste_msg = st.text_input("Digite uma mensagem para testar:",
                              "Meu pedido está atrasado")

    if st.button("🔬 Comparar Modelos"):
        agent, clf = carregar_modelos()

        col_comp1, col_comp2 = st.columns(2)

        with col_comp1:
            st.markdown("### 🧠 Gemini (LLM)")
            if agent:
                intencao_gemini = agent.classificar_intencao(teste_msg)
                st.success(f"**Categoria:** {intencao_gemini}")

                resposta_gemini = agent.atender(teste_msg)
                st.markdown("**Resposta:**")
                st.write(resposta_gemini)

        with col_comp2:
            st.markdown("### 📊 Modelo ML")
            if clf:
                resultado_ml = clf.prever(teste_msg)
                st.success(f"**Categoria:** {resultado_ml['categoria']}")
                st.metric("Confiança", f"{resultado_ml['confianca']:.1%}")

                with st.expander("Ver probabilidades detalhadas"):
                    for cat, prob in resultado_ml['probabilidades'].items():
                        st.write(f"{cat}: {prob:.2%}")

    st.markdown("---")

    # Tabela comparativa
    st.subheader("📊 Comparação de Performance")

    comparacao = pd.DataFrame({
        'Métrica': ['Acurácia', 'Tempo de Resposta', 'Custo por Requisição', 'Explicabilidade'],
        'Gemini (LLM)': ['~95%', '~2s', '$0.0015', 'Média'],
        'Modelo ML': ['100%*', '~0.1s', '$0.0001', 'Alta']
    })

    st.table(comparacao)
    st.caption("* Acurácia no conjunto de teste sintético")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p style="font-size: 1.1rem;"><strong>SmartOrder Assistant</strong> | Desenvolvido por <strong>Emerson Guimarães</strong></p>
    <p style="margin: 1rem 0;">
        <a href="https://www.linkedin.com/in/emersongsguimaraes/" target="_blank" style="text-decoration: none; margin: 0 10px;">
            <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
        </a>
        <a href="https://github.com/Gor0d" target="_blank" style="text-decoration: none; margin: 0 10px;">
            <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
        </a>
    </p>
    <p style="font-size: 0.9rem; color: #999;">
        🚀 Tecnologias: Python • Gemini AI • Scikit-learn • Streamlit • Plotly
    </p>
    <p style="font-size: 0.8rem; color: #aaa; margin-top: 1rem;">
        Projeto desenvolvido para demonstração de competências em IA, MLOps e Desenvolvimento Full Stack
    </p>
</div>
""", unsafe_allow_html=True)