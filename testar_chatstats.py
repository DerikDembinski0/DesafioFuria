from app import create_app, db
from app.models.user import User, ChatStats

app = create_app()

with app.app_context():
    for stat in ChatStats.query.all():
        user = User.query.get(stat.user_id)
        print(f"{user.nick}: {stat.total_mensagens}")
