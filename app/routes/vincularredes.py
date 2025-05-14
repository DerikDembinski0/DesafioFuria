from flask import Blueprint, redirect, request, session, current_app
import requests
from requests_oauthlib import OAuth1Session

vincularredes = Blueprint("vincularredes", __name__)

# ======== DISCORD CONFIGURAÇÃO ========
DISCORD_CLIENT_ID = "1371862389137473628"
DISCORD_CLIENT_SECRET = "LKezsdjFUqYWC_PPYrrcXu-YQkymOeKx"
DISCORD_REDIRECT_URI = "http://localhost:5000/painel"

# ======== TWITTER CONFIGURAÇÃO ========
TWITTER_CONSUMER_KEY = "QkJId3MtTkRtejJVSUU5bUVDdXg6MTpjaQ"
TWITTER_CONSUMER_SECRET = "lkJznGLZ-GF0F8P5-0xgvuCyop2cYehlinyZ8mbvIo4GOy28Qq"
TWITTER_CALLBACK_URL = "http://localhost:5000/twitter/callback"

# ======== ROTAS DISCORD ========

@vincularredes.route("/discord/login")
def discord_login():
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&scope=identify%20email"
    )
    return redirect(discord_auth_url)

@vincularredes.route("/painel")
def discord_callback():
    code = request.args.get("code")

    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "scope": "identify email",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    r.raise_for_status()
    access_token = r.json()["access_token"]

    user_info = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    return f"""
    <h2>Conta do Discord conectada com sucesso!</h2>
    <p><strong>Username:</strong> {user_info['username']}#{user_info['discriminator']}</p>
    <p><strong>ID:</strong> {user_info['id']}</p>
    <p><strong>Email:</strong> {user_info.get('email', 'Não disponível')}</p>
    """

# ======== ROTAS TWITTER ========

@vincularredes.route("/twitter/login")
def twitter_login():
    twitter = OAuth1Session(
        TWITTER_CONSUMER_KEY,
        client_secret=TWITTER_CONSUMER_SECRET,
        callback_uri=TWITTER_CALLBACK_URL
    )
    request_token = twitter.fetch_request_token("https://api.twitter.com/oauth/request_token")
    session["request_token"] = request_token
    auth_url = twitter.authorization_url("https://api.twitter.com/oauth/authorize")
    return redirect(auth_url)

@vincularredes.route("/twitter/callback")
def twitter_callback():
    request_token = session.pop("request_token")
    twitter = OAuth1Session(
        TWITTER_CONSUMER_KEY,
        client_secret=TWITTER_CONSUMER_SECRET,
        resource_owner_key=request_token["oauth_token"],
        resource_owner_secret=request_token["oauth_token_secret"],
        verifier=request.args.get("oauth_verifier")
    )
    access_token = twitter.fetch_access_token("https://api.twitter.com/oauth/access_token")

    return f"""
    <h2>Conta do Twitter conectada com sucesso!</h2>
    <p><strong>@{access_token['screen_name']}</strong></p>
    <p><strong>ID:</strong> {access_token['user_id']}</p>
    """
