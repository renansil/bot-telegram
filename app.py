import time
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import mercadopago
import telebot
import base64
from PIL import Image
from io import BytesIO
from flask import Flask, redirect, render_template, request
import sqlite3

# Tokens de acesso
TOKEN = 'APP_USR-3040450919486654-102317-a8ad886afe0f7bc61c9fe8206eb9884c-1951389235'
TOKEN_BOT = '7301751226:AAFvHwIBo7LNKWzCZDd6-tIhGsBiWcRBzdM'

# Configuração do SDK e Bot
sdk = mercadopago.SDK(TOKEN)
bot = telebot.TeleBot(TOKEN_BOT)
app = Flask(__name__)

serie_link = 'https://t.me/flexplaytv'

# Função para criar a tabela no banco de dados SQLite
def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        user_id INTEGER)''')
    conn.commit()
    conn.close()

# Função para salvar o user_id no banco de dados
def save_user_id(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id  # Captura o user_id do usuário
    save_user_id(user_id)  # Armazena o user_id no banco de dados

    # Criação do botão de miniapp
    keyboard = InlineKeyboardMarkup()
    btn_miniapp = InlineKeyboardButton(
        "INICIAR APP", 
        web_app={"url": "https://bot-telegram-production-25b9.up.railway.app/"}
    )
    keyboard.add(btn_miniapp)

    # Envia a mensagem com o botão
    bot.send_message(
        user_id, 
        "Bem-vindo! Clique em INICIAR APP para assistir sua série.", 
        reply_markup=keyboard
    )

def create_payment(value):
    expire = datetime.datetime.now() + datetime.timedelta(days=1)
    expire = expire.strftime("%Y-%m-%dT%-H:%M:%S.000-03:00")

    payment_data = {
        "transaction_amount": int(value),
        "payment_method_id": 'pix',
        "installments": 1,
        "description": 'Descrição',
        "date_of_expiration": f"{expire}",
    }
    result = sdk.payment().create(payment_data)
    return result

def enviar_pagamento(user_id, valor):
    payment = create_payment(valor)
    pix_copia_cola = payment['response']['point_of_interaction']['transaction_data']['qr_code']
    qr_code_base64 = payment['response']['point_of_interaction']['transaction_data']['qr_code_base64']

    qr_code = base64.b64decode(qr_code_base64)
    qr_code_img = Image.open(BytesIO(qr_code))
    qrcode_output = qr_code_img.convert('RGB')

    texto = (
        "📸 QR-CODE\n\n"
        "💰 Valor a Pagar: R$ 8\n"
        "⏳ Prazo Para Pagamento: 15 Minutos\n\n"
        "💠 Pix Copia e cola:\n\n"
        "👇👇\n"
        f"<code>{pix_copia_cola}</code>"
    )

    keyboard = InlineKeyboardMarkup()
    btn_pagamento = InlineKeyboardButton("Já paguei!", callback_data=f"pagamento_efetuado_{payment['response']['id']}_{serie_link}")
    keyboard.add(btn_pagamento)

    bot.send_photo(user_id, qrcode_output, caption=texto, parse_mode='HTML', reply_markup=keyboard)

# Verifica o status do pagamento
def pagamento_confirmado(payment_id):
    payment = sdk.payment().get(payment_id)
    status = payment['response'].get('status')
    return status == "approved"

# Callback do botão "Já paguei!"
@bot.callback_query_handler(func=lambda call: call.data.startswith("pagamento_efetuado_"))
def verificar_pagamento(call):
    payment_id, serie_link = call.data.split("_")[2], call.data.split("_")[3]
    user_id = call.from_user.id
    if pagamento_confirmado(payment_id):
        bot.send_message(user_id, "✅ Pagamento Confirmado!\nAcesse sua série aqui:")
        bot.send_message(user_id, serie_link)
    else:
        bot.send_message(user_id, "❌ Pagamento não encontrado. Tente novamente em alguns minutos.")

@app.route('/')
def index():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users ORDER BY id DESC LIMIT 1')
    user_id = cursor.fetchone()
    conn.close()

    if user_id:
        return render_template('index.html', user_id=user_id[0])
    else:
        return "Erro: Nenhum usuário encontrado.", 400

@app.route('/pagar', methods=['POST'])
def iniciar_pagamento():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users ORDER BY id DESC LIMIT 1')
    user_id = cursor.fetchone()
    conn.close()

    if user_id:
        enviar_pagamento(user_id[0], 8)  # Envia o pagamento para o user_id
        return redirect("https://t.me/flexplaytv_bot")  # Redireciona para o bot
    else:
        return "Erro: Nenhum usuário encontrado.", 400

# Endpoint do Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)  # Converte a atualização recebida do Telegram em um objeto
    bot.process_new_updates([update])  # Processa a atualização através do bot
    return '', 200  # Retorna um status de sucesso para o Telegram

if __name__ == "__main__":
    create_db()  # Cria o banco de dados ao iniciar o app

    # Configuração do Webhook
    WEBHOOK_URL = "https://bot-telegram-production-25b9.up.railway.app/webhook"  # Substitua pelo seu domínio do Railway ou onde o Flask estiver hospedado
    bot.remove_webhook()  # Remove webhook anterior, se houver
    bot.set_webhook(url=WEBHOOK_URL)  # Define o webhook com o URL do seu servidor

    print(f"Webhook configurado: {WEBHOOK_URL}")

    # Inicia o Flask
    app.run(host="0.0.0.0", port=8000)
