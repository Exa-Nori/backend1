from flask import Flask, send_from_directory, jsonify, request
import requests

app = Flask(__name__, static_folder='public')

# Главная страница
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# API роут
@app.route('/api/services', methods=['GET'])
def services():
    return jsonify({
        'services': [
            "Уход за пожилыми",
            "Медицинский уход",
            "Бытовая помощь",
            "Психологическая поддержка"
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# Отправка сообщений в тг бота
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.form  # Данные из формы
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not all([name, email, message]):
        return jsonify({"status": "error", "message": "Заполните все поля!"}), 400
    
    return jsonify({"status": "success", "message": "Сообщение отправлено!"})

TELEGRAM_BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"
TELEGRAM_CHAT_ID = "ВАШ_CHAT_ID"

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.form
    text = f"Новое сообщение:\nИмя: {data['name']}\nEmail: {data['email']}\nСообщение: {data['message']}"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    requests.post(url, json=payload)
    
    return jsonify({"status": "success"})


    