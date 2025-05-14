from flask import Blueprint, request, session, redirect, url_for, render_template
from flask_mail import Message
from app import mail
import uuid
from app.models.user import User
from app.models.pending_user import PendingUser
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import requests
from requests_oauthlib import OAuth1Session
import os

auth = Blueprint('auth', __name__)

# ===== Discord Config =====
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI")

# ===== Twitter Config =====
TWITTER_CONSUMER_KEY = os.environ.get("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.environ.get("TWITTER_CONSUMER_SECRET")
TWITTER_CALLBACK_URL = os.environ.get("TWITTER_CALLBACK_URL")

@auth.before_app_request
def limpar_pendentes_expirados():
    limite = datetime.utcnow() - timedelta(hours=24)
    expirados = PendingUser.query.filter(PendingUser.criado_em < limite).all()
    for p in expirados:
        db.session.delete(p)
    if expirados:
        db.session.commit()

@auth.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')
    manter = request.form.get('manter')

    if not email or not senha:
        return 'E-mail e senha obrigatórios.', 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(senha):
        return 'E-mail ou senha inválidos.', 403

    session['user'] = user.email
    session['vip'] = user.is_vip

    if manter:
        session.permanent = True
        from datetime import timedelta
        auth.permanent_session_lifetime = timedelta(days=30)

    return redirect(url_for('main.chat'))


@auth.route('/auth/confirm')
def confirm():
    token = request.args.get('token')
    pending = PendingUser.query.filter_by(token=token).first()

    if not pending:
        return 'Token inválido ou expirado.', 403

    if User.query.filter_by(email=pending.email).first():
        db.session.delete(pending)
        db.session.commit()
        return 'Usuário já confirmado anteriormente.', 400

    novo_user = User(
        nome=pending.nome,
        nascimento=pending.nascimento,
        nick=pending.nick,
        email=pending.email,
        senha_hash=pending.senha_hash,
        is_vip=False
    )
    db.session.add(novo_user)
    db.session.delete(pending)
    db.session.commit()

    session['user'] = novo_user.email
    session['vip'] = novo_user.is_vip

    return redirect(url_for('main.chat'))


@auth.route('/admin/promover', methods=['POST'])
def promover_vip():
    email = request.form.get('email')
    if not email:
        return 'Email não fornecido.', 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return f'Usuário {email} não encontrado.', 404

    user.is_vip = True
    db.session.commit()
    return f'Usuário {email} agora é VIP!', 200


@auth.route('/admin/remover', methods=['POST'])
def remover_vip():
    email = request.form.get('email')
    if not email:
        return 'Email não fornecido.', 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return f'Usuário {email} não encontrado.', 404

    user.is_vip = False
    db.session.commit()
    return f'VIP removido de {email} com sucesso!', 200


@auth.route('/admin')
def admin_panel():
    return render_template('admin.html')


@auth.route('/criar-conta', methods=['POST'])
def criar_conta_post():
    nome = request.form.get('nome')
    nascimento = request.form.get('nascimento')
    nick = request.form.get('nick')
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not all([nome, nascimento, nick, email, senha]):
        return 'Todos os campos são obrigatórios.', 400

    if User.query.filter_by(email=email).first() or PendingUser.query.filter_by(email=email).first():
        return 'Usuário já existe ou está aguardando confirmação.', 400

    senha_hash = generate_password_hash(senha)
    token = str(uuid.uuid4())

    pendente = PendingUser(
        nome=nome,
        nascimento=nascimento,
        nick=nick,
        email=email,
        senha_hash=senha_hash,
        token=token
    )
    db.session.add(pendente)
    db.session.commit()

    confirm_link = f"http://localhost:5000/auth/confirm?token={token}"

    html_body = f"""
    <p>Olá, <strong>{nick}</strong>!</p>
    <p>Clique no botão abaixo para ativar sua conta no FURIA Chat:</p>
    <div style='margin-top: 20px; margin-bottom: 30px;'>
      <a href='{confirm_link}' style='background-color: #FFD700; color: #000; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;'>
        Confirmar Conta
      </a>
    </div>
    <p>Se você não solicitou este cadastro, ignore esta mensagem.</p>
    <p>FURIA Team ⚡</p>
    """

    msg = Message(
        subject='🧑‍🤝 Confirme seu cadastro no FURIA Chat',
        sender='noreply@furia.gg',
        recipients=[email],
        html=html_body
    )

    try:
        mail.send(msg)
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        return "Erro ao enviar e-mail. Tente novamente mais tarde.", 500

    return render_template('confirmacao.html', email=email)


@auth.route('/discord/login')
def discord_login():
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&scope=identify%20email"
    )
    return redirect(discord_auth_url)


@auth.route('/auth/discord/callback')
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

    email = session.get("user")
    user = User.query.filter_by(email=email).first()
    if user:
        user.discord_id = user_info["id"]
        db.session.commit()

    return redirect(url_for('main.painel'))


@auth.route('/twitter/login')
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


@auth.route('/auth/twitter/callback')
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

    email = session.get("user")
    user = User.query.filter_by(email=email).first()
    if user:
        user.twitter_id = access_token["user_id"]
        db.session.commit()

    return redirect(url_for('main.painel'))


@auth.route("/logout", methods=["POST"])
def logout():
    print("➡️ Logout acionado no servidor")
    session.clear()
    return render_template("index.html")

