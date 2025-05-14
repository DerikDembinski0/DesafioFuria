from app import create_app
import os
import requests
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv, find_dotenv

# 🔍 Localiza e carrega o .env
env_path = find_dotenv()
print(f"📦 .env detectado em: {env_path}")
load_dotenv(env_path, override=True)

# Cria app Flask com contexto
app = create_app()

with app.app_context():
    print("\n🔐 Testando credenciais...")

    # DISCORD
    DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
    DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
    DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI")

    print("\n🌐 Conectando ao Discord...")
    print("🚨 VALOR DE DISCORD_CLIENT_ID =", DISCORD_CLIENT_ID)

    discord_data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": "CÓDIGO_FAKE",  # apenas para testar requisição
        "redirect_uri": DISCORD_REDIRECT_URI,
        "scope": "identify email"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        r = requests.post("https://discord.com/api/oauth2/token", data=discord_data, headers=headers)
        print("✅ Requisição enviada com sucesso (mesmo com código inválido)")
        print("Status:", r.status_code)
        print("Resposta esperada (erro 400):", r.json())
    except Exception as e:
        print("❌ Falha ao conectar ao Discord:", e)

    # TWITTER
    TWITTER_CONSUMER_KEY = os.environ.get("TWITTER_CONSUMER_KEY")
    TWITTER_CONSUMER_SECRET = os.environ.get("TWITTER_CONSUMER_SECRET")
    TWITTER_CALLBACK_URL = os.environ.get("TWITTER_CALLBACK_URL")

    print("\n🌐 Conectando ao Twitter...")

    try:
        twitter = OAuth1Session(
            TWITTER_CONSUMER_KEY,
            client_secret=TWITTER_CONSUMER_SECRET,
            callback_uri=TWITTER_CALLBACK_URL
        )
        request_token = twitter.fetch_request_token("https://api.twitter.com/oauth/request_token")
        print("✅ Twitter retornou o request_token com sucesso!")
        print("oauth_token:", request_token["oauth_token"])
    except Exception as e:
        print("❌ Falha ao conectar ao Twitter:", e)
