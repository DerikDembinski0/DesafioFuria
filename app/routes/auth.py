from flask import Blueprint, request, session, redirect, url_for, render_template
from flask_mail import Message
from app import mail
import uuid
from app.models.user import User
from app.models.pending_user import PendingUser
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)

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
        subject='🦁 Confirme seu cadastro no FURIA Chat',
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
