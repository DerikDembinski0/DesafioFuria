from app import socketio
from flask_socketio import emit
from flask import request
from app import db
from app.models.user import User, ChatStats
  # ou o caminho correto se seus modelos estiverem em outro lugar


@socketio.on('connect')
def handle_connect():
    print(f'🟢 Novo usuário conectado: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'🔴 Usuário desconectado: {request.sid}')

@socketio.on('message')
def handle_message(data):
    """
    Espera um dicionário com as chaves:
    - nick: str
    - vip: bool
    - hora: str (formato HH:MM)
    - texto: str
    """
    print(f'📩 {data["hora"]} - {"[VIP] " if data["vip"] else ""}{data["nick"]}: {data["texto"]}')
    emit('message', data, broadcast=True)


@socketio.on("message")
def handle_message(data):
    msg = data["texto"]         # 👈 isso aqui muda de "msg" para "texto"
    nick = data["nick"]

    user = User.query.filter_by(nick=nick).first()
    if user:
        stats = ChatStats.query.filter_by(user_id=user.id).first()
        if not stats:
            stats = ChatStats(user_id=user.id, total_mensagens=1)
            db.session.add(stats)
        else:
            stats.total_mensagens += 1
        db.session.commit()

    emit("message", data, broadcast=True)

