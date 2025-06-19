from flask import Flask, send_from_directory, jsonify, request
import requests

app = Flask(__name__, static_folder='public')

# Главная страница
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# API для списка услуг
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

# Новый API для отправки данных в Telegram
@app.route('/api/send-to-telegram', methods=['POST'])
def send_to_telegram():
    bot_token = "7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo"  # Токен бота
    chat_id = "719874188"  # Укажите правильный chat_id

    # Проверяем входящие данные
    data = request.json
    if not data or 'name' not in data or 'message' not in data:
        return jsonify({"error": "Пожалуйста, заполните все поля (name и message)!"}), 400

    # Формируем сообщение для Telegram
    telegram_message = f"""
📝 *Новая заявка с формы сайта* 📝
👤 *Имя*: {data['name']}
📧 *Email*: {data.get('email', 'Не указан')}
💬 *Сообщение*: {data['message']}
    """

    # Печатаем для проверки запросов в логах (поможет с отладкой)
    print(f"Отправка сообщения: {telegram_message}")

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": telegram_message,
                "parse_mode": "Markdown"
            }
        )
        # Логи успешного отправления
        print(f"Telegram ответ: {response.json()}")

        if response.status_code == 200:
            return jsonify({"success": True})
        else:
            return jsonify({"error": response.json()}), 500
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)