from flask import Flask, send_from_directory, request, jsonify
import requests
import logging
from flask_compress import Compress

app = Flask(__name__, static_folder="public")
Compress(app)
logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/api/send-to-telegram', methods=['POST'])
def send_to_telegram():
    bot_token = "6847127004:AAHJ8N5td3PAm40KJh2kY_2rMoCI72th4qg"
    chat_id = "719874188"

    data = request.get_json()
    if not data or 'name' not in data or 'message' not in data:
        return jsonify({"error": "Пожалуйста, заполните имя и сообщение"}), 400

    # Include email if provided
    email_text = f"\n📧 Email: {data['email']}" if data.get('email') else ""
    
    telegram_message = f"""📝 Новое сообщение с сайта L'ÎLE DE RÊVE

👤 Имя: {data['name']}{email_text}
💬 Сообщение: {data['message']}

---
Отправлено: {data.get('timestamp', 'не указано')}"""

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": telegram_message},
            timeout=10
        )
        
        # Логируем ответ Телеграма
        logging.debug(f"Telegram API Response: {response.status_code}, {response.text}")
        
        if response.status_code == 200:
            return jsonify({"success": True, "message": "Сообщение успешно отправлено!"})
        else:
            logging.error(f"Telegram API Error: {response.text}")
            return jsonify({"error": "Ошибка при отправке сообщения в Telegram"}), 500
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Request Exception: {str(e)}")
        return jsonify({"error": "Ошибка соединения с Telegram"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Произошла неожиданная ошибка"}), 500

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True)
