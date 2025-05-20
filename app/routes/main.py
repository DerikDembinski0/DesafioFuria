from flask import Blueprint, render_template, session, redirect, url_for, request, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models.user import User, ChatStats
import os
import requests
from bs4 import BeautifulSoup
import feedparser

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

@main.route('/atualizar-twitch', methods=['POST'])
def atualizar_twitch():
    canal = request.form.get("canal")
    email = session.get("user")
    user = User.query.filter_by(email=email).first()
    if user and canal:
        user.twitch_channel = canal.strip().lower()
        db.session.commit()
    return redirect(url_for("main.painel"))

@main.route("/news")
def news():
    feed_url = 'https://www.hltv.org/rss/news'
    feed = feedparser.parse(feed_url)

    news_list = []
    max_to_show = 10

    for entry in feed.entries:
        title_lower = entry.title.lower()

        if title_lower.startswith("short news"):
            continue

        is_furia = "furia" in title_lower

        image_url = None
        if "media_content" in entry and len(entry.media_content) > 0:
            image_url = entry.media_content[0].get("url")

        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "date": entry.published,
            "is_furia": is_furia,
            "image": image_url
        })

        if len(news_list) >= max_to_show:
            break

    # 🔥 Adicionado: pega o usuário da sessão
    user = None
    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()

    return render_template("news.html", news_list=news_list, total=len(news_list), user=user)


@main.route("/ranking")
def ranking():
    email = session.get("user")
    user = User.query.filter_by(email=email).first() if email else None

    top_users = (
        ChatStats.query
        .join(User)
        .order_by(ChatStats.total_mensagens.desc())
        .limit(10)
        .all()
    )

    minha_posicao = None
    minhas_msgs = 0

    if user:
        all_users = (
            ChatStats.query
            .join(User)
            .order_by(ChatStats.total_mensagens.desc())
            .all()
        )
        for i, stat in enumerate(all_users, start=1):
            if stat.user_id == user.id:
                minha_posicao = i
                minhas_msgs = stat.total_mensagens
                break

    return render_template("ranking.html", top_users=top_users, minha_posicao=minha_posicao, minhas_msgs=minhas_msgs, user=user)
