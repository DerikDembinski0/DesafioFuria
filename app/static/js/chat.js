document.addEventListener("DOMContentLoaded", () => {
  const socket = io();

  const form = document.getElementById("chat-form");
  const input = document.getElementById("msg-input");
  const chatBox = document.getElementById("chat-box");
  const nick = document.body.dataset.nick;
  const isVip = document.body.dataset.vip === "true";
  const emojiButton = document.getElementById("emoji-button");

  // Criar seletor customizado
  const emojiPopup = document.createElement("div");
  emojiPopup.id = "emoji-popup";
  emojiPopup.style.position = "absolute";
  emojiPopup.style.bottom = "70px";
  emojiPopup.style.left = "20px";
  emojiPopup.style.padding = "10px";
  emojiPopup.style.background = "#222";
  emojiPopup.style.border = "2px solid yellow";
  emojiPopup.style.borderRadius = "10px";
  emojiPopup.style.display = "none";
  emojiPopup.style.flexWrap = "wrap";
  emojiPopup.style.maxWidth = "240px";
  emojiPopup.style.maxHeight = "200px";
  emojiPopup.style.overflowY = "auto";
  emojiPopup.style.zIndex = "9999";

  document.body.appendChild(emojiPopup);

  // Toggle visibilidade
  emojiButton.addEventListener("click", () => {
    emojiPopup.style.display = emojiPopup.style.display === "none" ? "flex" : "none";
  });

  // Fechar ao clicar fora
  document.addEventListener("click", (e) => {
    if (!emojiPopup.contains(e.target) && e.target !== emojiButton) {
      emojiPopup.style.display = "none";
    }
  });

  // Carregar emojis do JSON
  fetch("/static/js/emojis.json")
    .then(res => res.json())
    .then(data => {
      const emojis = data.populares || ["😂", "😮", "😍", "👏", "🔥","🤣","😭","😘",];
      emojis.forEach(emoji => {
        const span = document.createElement("span");
        span.textContent = emoji;
        span.style.fontSize = "22px";
        span.style.cursor = "pointer";
        span.style.margin = "5px";
        span.addEventListener("click", () => {
          input.value += emoji;
          input.focus();
        });
        emojiPopup.appendChild(span);
      });
    });

  // Enviar mensagem
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const msg = input.value.trim();
    if (msg) {
      const now = new Date();
      const hora = now.toLocaleTimeString("pt-BR", {
        hour: "2-digit",
        minute: "2-digit"
      });

      socket.emit("message", {
        nick: nick,
        vip: isVip,
        texto: msg,
        hora: hora
      });

      input.value = "";
    }
  });

  socket.on("message", function (data) {
    const msgDiv = document.createElement("div");
    const vipTag = data.vip ? "[VIP] " : "";
    msgDiv.textContent = `${data.hora} - ${vipTag}${data.nick}: ${data.texto}`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  });
});
