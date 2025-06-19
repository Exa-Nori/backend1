from flask import Flask, send_from_directory, jsonify, request
import requests

app = Flask(__name__, static_folder='public')

# Главная страница
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# API роут для списка услуг
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

# Новый API для отправки формы в Telegram
@app.route('/api/send-to-telegram', methods=['POST'])
def send_to_telegram():
    bot_token = "7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo"  # Ваш токен бота
    chat_id = "719874188"  # Укажите ваш чат ID в Telegram

    # Данные из тела запроса
    data = request.json
    if not data or 'name' not in data or 'message' not in data:
        return jsonify({"error": "Необходимо предоставить имя и сообщение"}), 400

    # Формируем сообщение для отправки в Telegram
    telegram_message = f"""
📝 *Новая заявка с формы сайта* 📝
👤 *Имя*: {data['name']}
💬 *Сообщение*: {data['message']}
    """

    try:
        # Отправляем данные в Telegram API
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": telegram_message, "parse_mode": "Markdown"}
        )
        if response.status_code == 200:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Ошибка при отправке сообщения"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)