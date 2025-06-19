from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__, static_folder='public')

# Главная страница
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# API для отправки услуг (пример существующего роута)
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

# Новый API роут для отправки данных в Telegram
@app.route('/api/send-to-telegram', methods=['POST'])
def send_to_telegram():     
    bot_token = "7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo"
    chat_id = "719874188"  # Замените на ваш chat ID из Telegram
    data = request.json

    # Проверяем, что все поля заполнены
    if not all(key in data for key in ("name", "email", "message")):
        return jsonify({'error': "Все поля обязательны!"}), 400

    # Формируем сообщение для Telegram
    telegram_message = f"""
📝 *Новая заявка с формы сайта* 📝
👤 *Имя*: {data['name']}
📧 *Email*: {data['email']}
💬 *Сообщение*: {data['message']}
    """

    # Отправляем сообщение в Telegram
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, json={
        'chat_id': chat_id,
        'text': telegram_message,
        'parse_mode': 'Markdown'
    })

    if response.status_code == 200:
        return jsonify({'success': True})
    else:
        return jsonify({'error': "Не удалось отправить сообщение!"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)