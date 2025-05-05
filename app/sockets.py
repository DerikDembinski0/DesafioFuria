from app import socketio
from flask_socketio import emit
from flask import request

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
