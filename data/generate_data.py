import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('pt_BR')

# Categorias de problemas
CATEGORIAS = {
    'atraso': ['Meu pedido está atrasado', 'Quanto tempo ainda demora?', 'Pedido não chegou'],
    'produto': ['Veio item errado', 'Faltou um produto', 'Produto veio estragado'],
    'cancelamento': ['Quero cancelar o pedido', 'Como cancelo?', 'Pode cancelar pra mim?'],
    'pagamento': ['Cobrado em duplicidade', 'Não consigo pagar', 'Reembolso'],
    'duvida': ['Como funciona?', 'Qual o horário?', 'Aceita vale refeição?']
}


def gerar_conversas(n=1000):
    dados = []

    for _ in range(n):
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

    df = pd.DataFrame(dados)
    df.to_csv('data/raw/conversas.csv', index=False)
    print(f"✅ {n} conversas geradas em data/raw/conversas.csv")
    return df


if __name__ == "__main__":
    df = gerar_conversas(1000)
    print(df.head())
    print(f"\nDistribuição de categorias:\n{df['categoria'].value_counts()}")