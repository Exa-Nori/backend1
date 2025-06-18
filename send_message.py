import requests
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo" 
TELEGRAM_CHAT_ID = "-100123456789"         

@app.route('/send_message', methods=['POST'])
def send_message():
   
    required_fields = ['name', 'email', 'message']
    if not all(field in request.form for field in required_fields):
        return jsonify({
            "status": "error",
            "message": "Необходимо заполнить все поля: name, email, message"
        }), 400

    try:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        text = f"""
        📩 Новое сообщение с сайта:
        ├ Имя: {name}
        ├ Email: {email}
        └ Сообщение: {message}
        """

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "MarkdownV2"
            },
            timeout=10
        )

        response.raise_for_status()
        logger.info(f"Сообщение отправлено в Telegram: {text}")
        
        return jsonify({"status": "success"})

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к Telegram API: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Ошибка при отправке сообщения"
        }), 500
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Внутренняя ошибка сервера"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)