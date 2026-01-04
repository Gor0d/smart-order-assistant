import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os


class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        self.model = MultinomialNB()
        self.classes = None

    def treinar(self, df):
        """Treina o modelo com os dados"""

        print("🎯 Iniciando treinamento do modelo...")
        print(f"📊 Total de amostras: {len(df)}")

        # Preparar dados
        X = df['mensagem']
        y = df['categoria']

        self.classes = y.unique()
        print(f"📋 Categorias: {list(self.classes)}")

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"\n📚 Treino: {len(X_train)} | Teste: {len(X_test)}")

        # Vetorização
        print("\n🔄 Vetorizando textos...")
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        # Treinar
        print("🧠 Treinando modelo Naive Bayes...")
        self.model.fit(X_train_vec, y_train)

        # Avaliar
        y_pred = self.model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"\n{'=' * 60}")
        print(f"✅ ACURÁCIA DO MODELO: {accuracy:.2%}")
        print(f"{'=' * 60}")

        print("\n📊 RELATÓRIO DE CLASSIFICAÇÃO:")
        print(classification_report(y_test, y_pred))

        print("\n📈 MATRIZ DE CONFUSÃO:")
        cm = confusion_matrix(y_test, y_pred, labels=self.classes)
        print(pd.DataFrame(cm, index=self.classes, columns=self.classes))

        return accuracy

    def prever(self, mensagem):
        """Prevê a categoria de uma mensagem"""
        X = self.vectorizer.transform([mensagem])
        predicao = self.model.predict(X)[0]
        probabilidades = self.model.predict_proba(X)[0]

        return {
            'categoria': predicao,
            'confianca': max(probabilidades),
            'probabilidades': dict(zip(self.classes, probabilidades))
        }

    def salvar(self, path='models/'):
        """Salva o modelo treinado"""
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.model, f'{path}/model.pkl')
        joblib.dump(self.vectorizer, f'{path}/vectorizer.pkl')
        joblib.dump(self.classes, f'{path}/classes.pkl')
        print(f"\n💾 Modelo salvo em: {path}")

    def carregar(self, path='models/'):
        """Carrega modelo salvo"""
        self.model = joblib.load(f'{path}/model.pkl')
        self.vectorizer = joblib.load(f'{path}/vectorizer.pkl')
        self.classes = joblib.load(f'{path}/classes.pkl')
        print(f"📂 Modelo carregado de: {path}")


# Teste
if __name__ == "__main__":
    print("🚀 CLASSIFICADOR DE INTENÇÕES - IFOOD AI\n")

    # Carregar dados
    print("📁 Carregando dados...")
    df = pd.read_csv('data/raw/conversas.csv')

    # Treinar
    clf = IntentClassifier()
    clf.treinar(df)

    # Salvar
    clf.salvar()

    # Testes de previsão
    print("\n" + "=" * 60)
    print("🧪 TESTES DE PREVISÃO")
    print("=" * 60)

    testes = [
        "Meu pedido não chegou ainda",
        "Quanto tempo demora?",
        "Veio o produto errado",
        "Quero meu dinheiro de volta",
        "Como faço para cancelar?",
        "Qual o horário de funcionamento?"
    ]

    for mensagem in testes:
        resultado = clf.prever(mensagem)
        print(f"\n📝 Mensagem: '{mensagem}'")
        print(f"🎯 Categoria: {resultado['categoria']}")
        print(f"📊 Confiança: {resultado['confianca']:.1%}")

        # Top 3 probabilidades
        probs = sorted(resultado['probabilidades'].items(),
                       key=lambda x: x[1], reverse=True)[:3]
        print("   Top 3:")
        for cat, prob in probs:
            print(f"   - {cat}: {prob:.1%}")

    print("\n" + "=" * 60)
    print("✅ TREINAMENTO CONCLUÍDO!")
    print("=" * 60)