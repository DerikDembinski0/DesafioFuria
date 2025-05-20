import random
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.user import User, ChatStats

app = create_app()

with app.app_context():
    for i in range(1, 21):
        email = f"user{i}@furia.gg"
        user = User.query.filter_by(email=email).first()

        # Criar usuário se não existir
        if not user:
            user = User(
                nome=f"Usuário {i}",
                nascimento="2000-01-01",
                nick=f"FURIA_{i}",
                email=email,
                senha_hash=generate_password_hash("123"),
                is_vip=random.choice([True, False])
            )
            db.session.add(user)
            db.session.flush()  # garante que user.id estará disponível

        # Criar ChatStats se não existir
        if not ChatStats.query.filter_by(user_id=user.id).first():
            stat = ChatStats(
                user_id=user.id,
                total_mensagens=random.randint(5, 300)
            )
            db.session.add(stat)

    db.session.commit()
    print("✅ 20 usuários e estatísticas adicionados com sucesso!")
