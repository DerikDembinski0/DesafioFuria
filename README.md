# 🦁 FURIA Chat

Um sistema de **chat em tempo real** com área VIP, feito para fãs da FURIA e comunidade gamer!  
Desenvolvido com **Python (Flask)**, **Socket.IO** e **SQLite**, com **interface moderna e interativa**.

---

## 📦 O que tem nesse projeto?

✅ Chat público e chat VIP  
✅ Login, cadastro e confirmação de e-mail  
✅ Upload de foto de perfil  
✅ Botão para sair da conta  
✅ Chat com horário, apelido e tag de VIP  
✅ Player de Twitch personalizável  
✅ Link com Twitter (em desenvolvimento)  
✅ Página de administração para promover VIPs  
✅ Integração com banco de dados SQLite

---

## 🧠 Como esse projeto funciona?

Tudo roda no seu computador usando Python e Flask.  
Você abre no navegador e vê o chat funcionando de verdade com outras pessoas em tempo real (usando Socket.IO).

---

## 🛠️ Tecnologias usadas

| Ferramenta       | Para quê serve                          |
|------------------|-----------------------------------------|
| Python + Flask   | Servidor web                            |
| Flask-SocketIO   | Chat em tempo real                      |
| SQLite + SQLAlchemy | Banco de dados local                 |
| Flask-Mail       | Envio de e-mail para confirmação       |
| HTML + CSS       | Interface bonita e responsiva           |
| JavaScript       | Funções no navegador                    |

---

## Video do projeto

[![Assista ao vídeo](https://img.youtube.com/vi/dZfbgXXoLVM/maxresdefault.jpg)](https://www.youtube.com/watch?v=dZfbgXXoLVM)

## 🚀 Como rodar o projeto (passo a passo fácil)

```bash
# 1. Clone o projeto (ou baixe .zip)
git clone https://github.com/seunome/furia-chat.git
cd furia-chat

# 2. Crie e ative o ambiente virtual
python -m venv .venv

# (Windows)
.venv\Scripts\activate
# (Linux/macOS)
# source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Crie o arquivo .env com uma chave secreta
echo SECRET_KEY=qualquercoisa123 > .env

# 5. Recrie o banco de dados (roda no terminal interativo Python)
python -c "
from app import db, create_app;
app = create_app();
with app.app_context():
    db.drop_all()
    db.create_all()
"

# 6. Rode o servidor local
python run.py

# 7. Abra no navegador:
# http://localhost:5000
```

🧪 Testando o chat
* Crie uma conta

* Confirme pelo link enviado no console (simula um e-mail)

* Faça login

* Use o painel para alterar foto, vincular Twitch, etc

* Peça para o admin promover sua conta para VIP (ou faça manualmente no banco)

* Acesse o Chat VIP! 🎉



# 👨‍💻 Desenvolvedor
Feito por Derik Dembinski – um homem das trincheiras.
Quer contribuir ou mandar sugestões? Fique à vontade!

📚 Licença
Este projeto é open-source. Use como quiser, mas não copie e finja que é seu 😎
