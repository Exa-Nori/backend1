from flask import Flask, send_from_directory, request, jsonify
import requests
import logging
from flask_compress import Compress
import os

app = Flask(__name__, static_folder="public")
Compress(app)
logging.basicConfig(level=logging.DEBUG)

# You should move these to environment variables for securit
BOT_TOKEN = "7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo"
CHAT_ID = "5682979333"

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/api/test-telegram', methods=['GET'])
def test_telegram():
    """Test endpoint to check if Telegram bot is working"""
    try:
        # Test bot info
        bot_info_response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getMe",
            timeout=10
        )
        
        logging.debug(f"Bot info response: {bot_info_response.status_code}, {bot_info_response.text}")
        
        if bot_info_response.status_code != 200:
            return jsonify({
                "error": "Bot token is invalid",
                "bot_response": bot_info_response.text
            }), 400
        
        bot_data = bot_info_response.json()
        
        # Test sending a message
        test_message = "🔧 Тест соединения с ботом L'ÎLE DE RÊVE\n\nЕсли вы видите это сообщение, бот работает корректно!"
        
        send_response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": test_message},
            timeout=10
        )
        
        logging.debug(f"Send message response: {send_response.status_code}, {send_response.text}")
        
        if send_response.status_code == 200:
            return jsonify({
                "success": True,
                "message": "Test message sent successfully!",
                "bot_info": bot_data.get('result', {}),
                "chat_id": CHAT_ID
            })
        else:
            return jsonify({
                "error": "Failed to send test message",
                "bot_info": bot_data.get('result', {}),
                "send_response": send_response.text,
                "chat_id": CHAT_ID
            }), 400
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Request Exception: {str(e)}")
        return jsonify({"error": f"Network error: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/api/get-chat-id', methods=['GET'])
def get_chat_id():
    """Get recent updates to find your chat ID"""
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            updates = data.get('result', [])
            
            chat_ids = []
            for update in updates[-10:]:  # Get last 10 updates
                if 'message' in update:
                    chat = update['message']['chat']
                    chat_ids.append({
                        'chat_id': chat['id'],
                        'chat_type': chat['type'],
                        'title': chat.get('title', ''),
                        'username': chat.get('username', ''),
                        'first_name': chat.get('first_name', ''),
                        'last_name': chat.get('last_name', '')
                    })
            
            return jsonify({
                "success": True,
                "current_chat_id": CHAT_ID,
                "available_chats": chat_ids,
                "total_updates": len(updates)
            })
        else:
            return jsonify({
                "error": "Failed to get updates",
                "response": response.text
            }), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/send-to-telegram', methods=['POST'])
def send_to_telegram():
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
        # Log the attempt
        logging.info(f"Attempting to send message to chat_id: {CHAT_ID}")
        logging.info(f"Message content: {telegram_message[:100]}...")
        
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": telegram_message},
            timeout=10
        )
        
        # Detailed logging
        logging.info(f"Telegram API Response Status: {response.status_code}")
        logging.info(f"Telegram API Response Body: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('ok'):
                return jsonify({
                    "success": True, 
                    "message": "Сообщение успешно отправлено!",
                    "telegram_response": response_data
                })
            else:
                return jsonify({
                    "error": f"Telegram API error: {response_data.get('description', 'Unknown error')}",
                    "telegram_response": response_data
                }), 500
        else:
            return jsonify({
                "error": f"HTTP {response.status_code}: {response.text}",
                "status_code": response.status_code
            }), 500
            
    except requests.exceptions.Timeout:
        logging.error("Timeout when connecting to Telegram API")
        return jsonify({"error": "Timeout при подключении к Telegram"}), 500
    except requests.exceptions.ConnectionError:
        logging.error("Connection error when connecting to Telegram API")
        return jsonify({"error": "Ошибка соединения с Telegram"}), 500
    except requests.exceptions.RequestException as e:
        logging.error(f"Request Exception: {str(e)}")
        return jsonify({"error": f"Ошибка запроса: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Неожиданная ошибка: {str(e)}"}), 500

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True)

#Если не работает, откатить до обновлений еблана Артема