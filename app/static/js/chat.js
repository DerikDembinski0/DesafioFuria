const socket = io();

const form = document.getElementById("chat-form");
const input = document.getElementById("msg-input");
const chatBox = document.getElementById("chat-box");
const nick = document.body.dataset.nick;
const isVip = document.body.dataset.vip === "true";

form.addEventListener("submit", function (e) {
  e.preventDefault();
  const msg = input.value.trim();
  if (msg) {
    const now = new Date();
    const hora = now.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

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
