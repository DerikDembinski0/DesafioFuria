from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    nascimento = db.Column(db.String(10))  # YYYY-MM-DD
    nick = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=True)
    is_vip = db.Column(db.Boolean, default=False)
    foto_url = db.Column(
        db.String(255),
        nullable=True,
        default='/static/images/default_avatar.png'  # ✅ Foto padrão para novos usuários
    )
    twitter_id = db.Column(db.String(50), unique=True, nullable=True)  # ✅ ID do Twitter
    discord_id = db.Column(db.String(50), unique=True, nullable=True)  # ✅ ID do Discord
    twitch_channel = db.Column(db.String(100))

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)
