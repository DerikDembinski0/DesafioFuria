from flask import Blueprint, render_template, session, redirect, url_for, request, current_app
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.user import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/chat')
def chat():
    email = session.get('user')
    if not email:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=email).first()
    if not user:
        return redirect(url_for('main.index'))

    return render_template('chat.html', user=user, vip=user.is_vip)

@main.route('/chat-vip')
def chat_vip():
    email = session.get('user')
    if not email:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=email).first()
    if not user or not user.is_vip:
        return redirect(url_for('main.index'))

    return render_template('chat.html', user=user, vip=True)

@main.route('/criar-conta')
def criar_conta():
    return render_template('login.html', modo='criar')

@main.route('/login-form')
def login_form():
    return render_template('login.html', modo='login')

@main.route('/painel')
def painel():
    if 'user' not in session:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=session['user']).first()
    if not user:
        return redirect(url_for('main.index'))

    return render_template('minhaconta.html', user=user)

@main.route('/upload-foto', methods=['POST'])
def upload_foto():
    if 'user' not in session:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=session['user']).first()
    if not user:
        return redirect(url_for('main.index'))

    foto = request.files.get('foto')
    if not foto or foto.filename == '':
        return redirect(url_for('main.painel'))

    filename = secure_filename(foto.filename)
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    path = os.path.join(upload_folder, filename)
    foto.save(path)

    user.foto_url = f'/static/uploads/{filename}'
    db.session.commit()

    return redirect(url_for('main.painel'))

@main.route('/definir-live', methods=['POST'])
def definir_live():
    email = session.get('user')
    if not email:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=email).first()
    if not user:
        return redirect(url_for('main.index'))

    canal = request.form.get('twitch_channel')
    if canal:
        user.twitch_channel = canal.strip().lower()
        db.session.commit()

    return redirect(url_for('main.painel'))