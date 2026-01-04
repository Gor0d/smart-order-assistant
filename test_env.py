
import os
from dotenv import load_dotenv

print("🔍 Testando carregamento do .env...\n")

# Carregar .env
load_dotenv()

# Verificar se carregou
api_key = os.getenv('GOOGLE_API_KEY')

if api_key:
    print(f"✅ API Key encontrada!")
    print(f"📝 Primeiros caracteres: {api_key[:10]}...")
    print(f"📏 Tamanho: {len(api_key)} caracteres")
else:
    print("❌ API Key NÃO encontrada!")
    print("\n🔍 Verificando arquivo .env...")

    import pathlib

    env_path = pathlib.Path('.env')

    if env_path.exists():
        print(f"✅ Arquivo .env existe em: {env_path.absolute()}")
        print(f"\n📄 Conteúdo do arquivo:")
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    else:
        print(f"❌ Arquivo .env NÃO encontrado em: {env_path.absolute()}")
