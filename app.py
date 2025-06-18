import requests
from flask import Flask, request, jsonify, send_from_directory
import logging

app = Flask(__name__, static_folder='public')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация Telegram (замените на свои реальные значения)
TELEGRAM_BOT_TOKEN = "7585621279"
TELEGRAM_CHAT_ID = "719874188"

def escape_markdown(text):
    """Экранирование специальных символов MarkdownV2"""
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

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

@app.route('/send_message', methods=['POST'])
def send_message():
    # Проверка Content-Type
    if not request.is_json and not request.form:
        return jsonify({
            "status": "error",
            "message": "Неверный формат запроса"
        }), 400

    try:
        # Получаем данные из формы или JSON
        data = request.get_json() if request.is_json else request.form

        # Проверка обязательных полей
        required_fields = ['name', 'email', 'message']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "status": "error",
                "message": f"Не заполнены обязательные поля: {', '.join(missing_fields)}"
            }), 400

        # Подготовка данных
        name = escape_markdown(data['name'])
        email = escape_markdown(data['email'])
        message = escape_markdown(data['message'])

        # Формируем сообщение
        text = f"""
📩 *Новое сообщение с сайта:*
├ *Имя:* {name}
├ *Email:* {email}
└ *Сообщение:* {message}
        """.strip()

        # Отправляем в Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "MarkdownV2"
            },
            timeout=15
        )

        response.raise_for_status()
        if not response.json().get('ok'):
            raise Exception("Telegram API вернул ошибку")

        logger.info("Сообщение успешно отправлено в Telegram")
        return jsonify({
            "status": "success",
            "message": "Сообщение успешно отправлено"
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Ошибка соединения с Telegram"
        }), 502
        
    except Exception as e:
        logger.error(f"Ошибка обработки: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Внутренняя ошибка сервера"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



    