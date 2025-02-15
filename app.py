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
TOKEN = 'APP_USR-5844600626489892-021511-eaf07748b134cc2d3d693a2825d0234c-186245838'
TOKEN_BOT = '8193140436:AAEh7MLrnP23qIALktvkuHyirSXnO4JIiOw'  # Substitua pelo seu token

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

    add_serie_link(1, "https://t.me/+bcxnk4TBMk80ZGE5")
    add_serie_link(2, "https://t.me/+Gx6irhzoeRoyYmYx")
    add_serie_link(3, "https://t.me/+WnE-7pM53QI2Yzgx")
    add_serie_link(4, "https://t.me/+WnE-7pM53QI2Yzgx")
    add_serie_link(5, "https://t.me/+A4VWFX7QCOUzZDdh")
    add_serie_link(6, "https://t.me/+55mp_kQOmiwwOThh")
    add_serie_link(7, "https://t.me/+g_jTfBuA-BUyZWEx")
    add_serie_link(8, "https://t.me/+_km05zAZPR0yYzhh")
    add_serie_link(9, "https://t.me/+O3yqgE-hV-FjYjY5")
    add_serie_link(10, "https://t.me/+oO9im4xUbHgwYTAx")
    add_serie_link(11, "https://t.me/+6d9tNVN7ybtmZDVh")
    add_serie_link(12, "https://t.me/+oQySjiTe88lmNzY5")
    add_serie_link(13, "https://t.me/+7nZ8Fp1IjAYwMWQx")
    add_serie_link(14, "https://t.me/+kJgxPpbJBT9kZGEx")
    add_serie_link(15, "https://t.me/+vDHlcx4d5TpmMGEx")
    add_serie_link(16, "https://t.me/+QfA9drK4WzNhNTk5")
    add_serie_link(17, "https://t.me/+lHoaBK1vbME4ZDBh")
    add_serie_link(18, "https://t.me/+kECaU1kbV59mYzEx")
    add_serie_link(19, "https://t.me/+Z7e9gI96Aog2Yzdh")
    add_serie_link(20, "https://t.me/+TsNGdtxkrBM0YzRh")
    add_serie_link(21, "https://t.me/+ta3TurQmv9dlMDhh")
    add_serie_link(22, "https://t.me/+2a4hPRTioNY5ZTI5")
    add_serie_link(23, "https://t.me/+RQuFkDPiESAxZTQx")
    add_serie_link(24, "https://t.me/+HyuDlxYsOi5iNDRh")
    add_serie_link(25, "https://t.me/+a9NbgDqjQV1kYmJh")
    add_serie_link(26, "https://t.me/+gT0CYPMcvwUwNTUx")
    add_serie_link(27, "https://t.me/+UEII-d0qVyM4MDRh")
    add_serie_link(28, "https://t.me/+DLzdyDaaS484ODIx")
    add_serie_link(29, "https://t.me/+53vmQbRRDJlhMmUx")
    add_serie_link(30, "https://t.me/+qskICL7A-28zNWYx")
    add_serie_link(31, "https://t.me/+yA4qrFMeLWJjYmJh")
    add_serie_link(32, "https://t.me/+Y2yYEzXwa3lmZDQx")
    add_serie_link(33, "https://t.me/+d96AaCy3loVjODkx")
    add_serie_link(34, "https://t.me/+MntZepNlKJlmMTJh")
    add_serie_link(35, "https://t.me/+Y3h8bqV7vdJlMGVh")
    add_serie_link(36, "https://t.me/+PGKRtG-ui8pkZGFh")
    add_serie_link(37, "https://t.me/+g97Ek47J_bQ3MjUx")
    add_serie_link(38, "https://t.me/+1U_3xp5bT9VhNzdh")
    add_serie_link(39, "https://t.me/+aEepldAMIlxlODcx")
    add_serie_link(40, "https://t.me/+Oqg2T9rnwHQ2MTQx")
    add_serie_link(41, "https://t.me/+hrcUfWJXy31mYWQx")
    add_serie_link(42, "https://t.me/+Rb7xJW1CZX8zYjUx")
    add_serie_link(43, "https://t.me/+BxoTccQ4xQk1MTVh")
    add_serie_link(44, "https://t.me/+DFr4y5MXL41hZWUx")
    add_serie_link(45, "https://t.me/+psB4CnKoZG05NzEx")
    add_serie_link(46, "https://t.me/+FJQB8F7Ijc1kMzIx")
    add_serie_link(47, "https://t.me/+mSoO2FzXwpZlOWQ5")
    add_serie_link(48, "https://t.me/+wds2XUdGRTYzMjU5")
    add_serie_link(49, "https://t.me/+9BvHTPWOqJUzNTdh")
    add_serie_link(50, "https://t.me/+Z7AfOb4ula40YWMx")
    add_serie_link(51, "https://t.me/+3w4maedahtJlOGYx")
    add_serie_link(52, "https://t.me/+PljB6zYRXTI5YjEx")
    add_serie_link(53, "https://t.me/+Nj7nYLsMmIxhODFh")
    add_serie_link(54, "https://t.me/+AIwaqlg21_dkN2Qx")
    add_serie_link(55, "https://t.me/+TkGfNDzBiD8wZDJh")
    add_serie_link(56, "https://t.me/+UL6kCjUVvnpkY2Fh")
    add_serie_link(57, "https://t.me/+5EJu9QcHr6kwZjcx")
    add_serie_link(58, "https://t.me/+zwYzL_4btUk3MmNh")
    add_serie_link(59, "https://t.me/+TIwUQL0yMIU5ZDUx")
    add_serie_link(60, "https://t.me/+ICQkrT7HG4U0MmEx")
    add_serie_link(61, "https://t.me/+Dj59BhDE7RI5NWMx")
    add_serie_link(62, "https://t.me/+CD_g4POMhAdjZTgx")

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
        web_app=WebAppInfo(url="https://bot-telegram-production-65a1.up.railway.app/")
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
