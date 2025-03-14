import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,MenuButtonWebApp
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import datetime
import mercadopago
import telebot
import base64
from PIL import Image
from io import BytesIO
from flask import Flask, redirect, render_template, request, jsonify
import sqlite3

# Tokens de acesso
TOKEN = 'SEU_TOKEN_MP'
TOKEN_BOT = 'TOKEN_BOT'  # Substitua pelo seu token

# Configuração do SDK e Bot
sdk = mercadopago.SDK(TOKEN)
bot = telebot.TeleBot(TOKEN_BOT)
app = Flask(__name__)

# Função para criar as tabelas no banco de dados SQLite
def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        user_id INTEGER UNIQUE,
                        joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        serie_id INTEGER,
                        amount REAL,
                        status TEXT,
                        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS abandonment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        abandonment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id))''')
    conn.commit()
    conn.close()

    add_serie_link(1, "LINK DO GRUPO ONDE TEM A SERIE OU PRODUTO")

# Função para salvar o user_id no banco de dados
def save_user_id(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

# Função para adicionar um link de série ao banco de dados
def add_serie_link(serie_id, link):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO series (serie_id, link) VALUES (?, ?)', (serie_id, link))
    conn.commit()
    conn.close()

# Função para buscar o link da série no banco de dados
def get_serie_link(serie_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT link FROM series WHERE serie_id = ?', (serie_id,))
    link = cursor.fetchone()
    conn.close()
    return link[0] if link else None

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    save_user_id(user_id)  # Salva o user_id no banco de dados
    
    # Criando os botões
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton(
        "Abrir MiniApp",
        web_app=WebAppInfo(url="https://bot-telegram-production-af28.up.railway.app/")
    )
    
    # Adicionando o botão ao teclado
    markup.add(button)
    
    # Enviando a mensagem com o teclado
    bot.send_message(
        user_id,
        "Bem-vindo! Clique no botão abaixo para abrir o MiniApp.",
        reply_markup=markup
    )

# Função para criar pagamento
def create_payment(value):
    expire = datetime.datetime.now() + datetime.timedelta(days=1)
    expire = expire.strftime("%Y-%m-%dT%-H:%M:%S.000-03:00")

    payment_data = {
        "transaction_amount": int(value),
        "payment_method_id": 'pix',
        "installments": 1,
        "description": 'Descrição',
        "date_of_expiration": f"{expire}",
        "payer": {
            "email": 'renansilveira39@gmail.com'
        }
    }
    result = sdk.payment().create(payment_data)
    return result

# Função para enviar pagamento
def enviar_pagamento(user_id, valor, serie_id, serie_name):
    payment = create_payment(valor)
    pix_copia_cola = payment['response']['point_of_interaction']['transaction_data']['qr_code']
    qr_code_base64 = payment['response']['point_of_interaction']['transaction_data']['qr_code_base64']

    qr_code = base64.b64decode(qr_code_base64)
    qr_code_img = Image.open(BytesIO(qr_code))
    qrcode_output = qr_code_img.convert('RGB')

    serie_link = get_serie_link(serie_id)
    if not serie_link:
        bot.send_message(user_id, "Erro: Série não encontrada.")
        return

    texto = (
        f"📸 QR-CODE para a série: <b>{serie_name}</b>\n\n"
        "💰 Valor a Pagar: R$ 5\n"
        "⏳ Prazo Para Pagamento: 15 Minutos\n\n"
        "💠 Pix Copia e cola:\n\n"
        "👇👇\n"
        f"<code>{pix_copia_cola}</code>"
    )

    keyboard = InlineKeyboardMarkup()
    btn_pagamento = InlineKeyboardButton(
        "⌛ JÁ PAGUEI! ⌛", 
        callback_data=f"pagamento_efetuado_{payment['response']['id']}_{serie_id}"
    )
    btn_suporte = InlineKeyboardButton(
        "FALAR COM SUPORTE", 
        url="https://t.me/sraadm"
    )
    keyboard.add(btn_pagamento)
    keyboard.add(btn_suporte)

    bot.send_photo(user_id, qrcode_output, caption=texto, parse_mode='HTML', reply_markup=keyboard)
    
# Verifica o status do pagamento
def pagamento_confirmado(payment_id):
    payment = sdk.payment().get(payment_id)
    status = payment['response'].get('status')
    return status == "approved"

# Callback do botão "Já paguei!"
@bot.callback_query_handler(func=lambda call: call.data.startswith("pagamento_efetuado_"))
def verificar_pagamento(call):
    try:
        payment_id, serie_id = call.data.split("_")[2], int(call.data.split("_")[3])
        user_id = call.from_user.id
        if pagamento_confirmado(payment_id):
            serie_link = get_serie_link(serie_id)
            if serie_link:
                bot.send_message(user_id, "✅ Pagamento Confirmado!\nAcesse sua série aqui:")
                bot.send_message(user_id, serie_link)
            else:
                bot.send_message(user_id, "Erro: Link da série não encontrado.")
        else:
            bot.send_message(user_id, "❌ Pagamento não encontrado. Tente novamente em alguns minutos.")
    except Exception as e:
        bot.send_message(call.from_user.id, "Ocorreu um erro ao verificar o pagamento.")
        print(f"Erro no callback de pagamento: {e}")

# Página inicial do MiniApp
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

# Endpoint para iniciar pagamento
@app.route('/pagar', methods=['GET','POST'])
def iniciar_pagamento():
    try:
        # Recebe os dados do formulário
        serie_id = request.form.get('serie_id')
        serie_name = request.form.get('serie_name')  # Captura o nome da série
        
        if not serie_id or not serie_name:
            return jsonify({"error": "Dados da série incompletos."}), 400

        # Pega o último usuário no banco
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users ORDER BY id DESC LIMIT 1')
        user_id = cursor.fetchone()
        conn.close()

        if user_id:
            enviar_pagamento(user_id[0], 5, int(serie_id), serie_name)  # Passa o nome da série e o valor 
            return render_template('checkout.html')
        else:
            return jsonify({"error": "Nenhum usuário encontrado."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
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
    WEBHOOK_URL = "https://bot-telegram-production-65a1.up.railway.app/webhook"  # Substitua pelo domínio do Railway ou onde o Flask estiver hospedado

    # Decida dinamicamente entre Webhook e Polling
    USE_WEBHOOK = True  # Altere para False para usar polling em vez de webhook

    if USE_WEBHOOK:
        bot.remove_webhook()  # Remove webhook anterior, se houver
        bot.set_webhook(url=WEBHOOK_URL)  # Define o webhook com o URL do servidor
        print(f"Webhook configurado: {WEBHOOK_URL}")
        
        # Inicia o servidor Flask
        app.run(host="0.0.0.0", port=8000)
    else:
        bot.remove_webhook()  # Certifique-se de que o webhook está desativado
        print("Iniciando bot com polling...")
        bot.infinity_polling()
