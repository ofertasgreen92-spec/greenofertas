from flask import Flask, request, render_template_string
import requests
import os
import random

app = Flask(__name__)

# ================= CONFIGURAÇÃO =================
CHAT_TOKEN = "8587703294:AAG8rLwpGsCRnyHWDcZppMngOoFDUb6-5Ss"
CHAT_ID = "-1003695377425"
ARQUIVO_HISTORICO = "historico.txt"
ULTIMO_EMOJI = None

# ================= HISTÓRICO =================
def ja_publicado(link):
    if not os.path.exists(ARQUIVO_HISTORICO):
        return False
    with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        return link in f.read().splitlines()

def salvar_historico(link):
    with open(ARQUIVO_HISTORICO, "a", encoding="utf-8") as f:
        f.write(link + "\n")

# ================= PUBLICAR TELEGRAM =================
def publicar(link, texto, imagem=None):
    global ULTIMO_EMOJI
    emojis = ["🔥","🚨","💥","⚡","🛒","🎯","💎"]
    emoji = random.choice(emojis)
    while emoji == ULTIMO_EMOJI:
        emoji = random.choice(emojis)
    ULTIMO_EMOJI = emoji

    mensagem = f"{emoji} {texto}\n\n{link}"

    try:
        if imagem:
            url = f"https://api.telegram.org/bot{CHAT_TOKEN}/sendPhoto"
            payload = {
                "chat_id": CHAT_ID,
                "photo": imagem,
                "caption": mensagem,
                "parse_mode": "HTML"
            }
        else:
            url = f"https://api.telegram.org/bot{CHAT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": mensagem,
                "parse_mode": "HTML"
            }
        r = requests.post(url, data=payload)
        return r.status_code == 200
    except Exception as e:
        print("Erro Telegram:", e)
        return False

# ================= HTML INTERFACE MODERNA =================
HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Green Ofertas PRO - Publicação Manual</title>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
<style>
body {
    font-family: 'Roboto', sans-serif;
    background: linear-gradient(to right, #27ae60, #2ecc71);
    margin:0;
    padding:0;
}
.container {
    max-width: 800px;
    margin: 50px auto;
    background:white;
    padding: 30px 40px;
    border-radius: 15px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}
h2 {
    text-align: center;
    color:#27ae60;
}
label {
    font-weight: bold;
    display:block;
    margin-bottom:5px;
    margin-top:15px;
}
input[type="text"], textarea {
    width:100%;
    padding:12px;
    border-radius:8px;
    border:1px solid #ccc;
    font-size:16px;
    box-sizing:border-box;
}
button {
    background:#16a085;
    color:white;
    padding:15px 25px;
    border:none;
    border-radius:10px;
    font-size:16px;
    cursor:pointer;
    margin-top:15px;
    transition:0.3s;
}
button:hover {
    background:#1abc9c;
}
.mensagem {
    margin-top:20px;
    font-weight:bold;
    text-align:center;
}
</style>
</head>
<body>
<div class="container">
<h2>🚀 Green Ofertas PRO</h2>
<form method="POST">
<label for="link">Link do produto</label>
<input type="text" name="link" id="link" placeholder="https://..." required>

<label for="texto">Texto da publicação</label>
<textarea name="texto" id="texto" rows="4" placeholder="Digite sua mensagem" required></textarea>

<label for="imagem">Imagem (opcional, URL)</label>
<input type="text" name="imagem" id="imagem" placeholder="https://...">

<button type="submit" name="acao" value="publicar">📤 Publicar no Telegram</button>
</form>

<div class="mensagem">
{{ mensagem }}
</div>
</div>
</body>
</html>
"""

# ================= ROUTE =================
@app.route("/", methods=["GET","POST"])
def index():
    mensagem = ""
    if request.method == "POST":
        acao = request.form.get("acao")
        if acao == "publicar":
            link = request.form.get("link")
            texto = request.form.get("texto")
            imagem = request.form.get("imagem") or None

            if not ja_publicado(link):
                if publicar(link, texto, imagem):
                    salvar_historico(link)
                    mensagem = "✅ Publicado com sucesso!"
                else:
                    mensagem = "❌ Erro ao publicar."
            else:
                mensagem = "⚠️ Link já publicado."

    return render_template_string(HTML, mensagem=mensagem)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1030))
    app.run(host="0.0.0.0", port=port)