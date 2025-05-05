from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from dotenv import load_dotenv
import os
from datetime import timedelta

# SocketIO com CORS liberado
socketio = SocketIO(cors_allowed_origins="*")
db = SQLAlchemy()
mail = Mail()

def create_app():
    load_dotenv()
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/users.db'

    # Configuração do Mailtrap SMTP atualizado
    app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_USERNAME'] = 'b2f94fbff81a35'
    app.config['MAIL_PASSWORD'] = 'e1d61f892b26bd'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    app.permanent_session_lifetime = timedelta(days=30)

    db.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)

    from app.routes.main import main
    from app.routes.auth import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    # ⚠️ ESSENCIAL PARA FUNCIONAMENTO DO CHAT
    from app import sockets

    return app
