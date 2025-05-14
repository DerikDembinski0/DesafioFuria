from app import db
from app import create_app

app = create_app()

with app.app_context():
    print("⛔ Apagando tabelas existentes...")
    db.drop_all()
    print("✅ Tabelas apagadas.")
    print("📦 Criando novas tabelas...")
    db.create_all()
    print("✅ Banco de dados recriado com sucesso!")

