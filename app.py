from flask import Flask, send_from_directory, request, jsonify
import requests

app = Flask(__name__, static_folder="public")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/send-to-telegram", methods=["POST"])
def send_to_telegram():
    bot_token = "7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo"
    chat_id = "719874188"   # Укажите свой Telegram Chat ID.

    # Получение данных из запроса
    data = request.json
    if not data or 'name' not in data or 'message' not in data:
        return jsonify({"error": "Обязательные поля: name и message."}), 400

    # Сообщение для Telegram
    telegram_message = f"""
📝 *Новая заявка с формы сайта:*
👤 *Имя*: {data['name']}
📧 *Email*: {data.get('email', 'Не указан')}
💬 *Сообщение*: {data['message']}
    """

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": telegram_message,
                "parse_mode": "Markdown"
            }
        )
        if response.status_code == 200:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": response.json()}), 500
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)