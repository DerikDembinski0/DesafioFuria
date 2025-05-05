from app import db

class PendingUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    nascimento = db.Column(db.String(10))
    nick = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    criado_em = db.Column(db.DateTime, server_default=db.func.now())
