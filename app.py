from flask import Flask, send_from_directory, request, jsonify, make_response
import requests
import logging
from flask_compress import Compress
import re
import uuid
import html
from functools import wraps
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from config import get_config

# Получение и валидация конфигурации
Config = get_config()
Config.validate()

app = Flask(__name__, static_folder="public")

# Настройка Flask
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.config['SESSION_COOKIE_SECURE'] = Config.SESSION_COOKIE_SECURE
app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE

# Инициализация расширений
Compress(app)

# Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[f"{Config.RATE_LIMIT_PER_HOUR} per hour"]
)

# Security Headers с Talisman
csp_string = "; ".join([f"{k} {v}" for k, v in Config.CSP_POLICY.items()])
talisman = Talisman(
    app,
    force_https=not Config.DEBUG,
    strict_transport_security=True,
    content_security_policy=csp_string,
    feature_policy={
        'camera': "'none'",
        'microphone': "'none'",
        'geolocation': "'none'"
    }
)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Валидаторы
def sanitize_input(value: str) -> str:
    """Очистка входных данных от потенциально опасного контента"""
    if not isinstance(value, str):
        return str(value)
    
    # HTML escape
    value = html.escape(value)
    
    # Удаление управляющих символов
    value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
    
    # Ограничение длины
    return value[:10000]  # Максимум 10k символов

def validate_email(email: str) -> bool:
    """Валидация email адреса"""
    if not email:
        return True  # Email опциональный
    
    email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) <= Config.MAX_EMAIL_LENGTH

def validate_phone(phone: str) -> bool:
    """Валидация российского номера телефона"""
    if not phone:
        return False
    
    phone = phone.strip()
    # Удаляем все символы кроме цифр и +
    cleaned_phone = re.sub(r'[^\d+]', '', phone)
    
    if len(cleaned_phone) > Config.MAX_PHONE_LENGTH:
        return False
    
    return bool(re.match(r'^\+?7[0-9]{10}$|^8[0-9]{10}$', cleaned_phone))

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Optional[str]:
    """Валидация обязательных полей"""
    for field in required_fields:
        value = data.get(field)
        if not value or (isinstance(value, str) and not value.strip()):
            return f"Поле '{field}' обязательно для заполнения"
    return None

def validate_field_length(data: Dict[str, Any], field: str, max_length: int) -> Optional[str]:
    """Валидация длины поля"""
    value = data.get(field, '')
    if len(str(value)) > max_length:
        return f"Поле '{field}' не должно превышать {max_length} символов"
    return None

def validate_no_suspicious_content(text: str) -> bool:
    """Проверка на подозрительный контент"""
    if not text:
        return True
    
    # Проверка на SQL инъекции
    sql_patterns = [
        r'(union\s+select|select\s+.*\s+from|insert\s+into|update\s+.*\s+set|delete\s+from)',
        r'(drop\s+table|create\s+table|alter\s+table)',
        r'(exec\s*\(|execute\s*\(|sp_)',
        r'(script\s*>|javascript:|vbscript:)',
        r'(<script|</script>|<iframe|</iframe>)',
    ]
    
    text_lower = text.lower()
    for pattern in sql_patterns:
        if re.search(pattern, text_lower):
            return False
    
    return True

# Декораторы
def security_headers(f):
    """Декоратор для добавления дополнительных security headers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['X-Request-ID'] = str(uuid.uuid4())
        response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        return response
    return decorated_function

def log_security_event(event_type: str, details: str, client_ip: str):
    """Логирование событий безопасности"""
    logger.warning(f"SECURITY_EVENT: {event_type} | IP: {client_ip} | Details: {details}")

def handle_telegram_errors(f):
    """Декоратор для обработки ошибок Telegram API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = get_remote_address()
        try:
            return f(*args, **kwargs)
        except requests.exceptions.Timeout as e:
            log_security_event("TELEGRAM_TIMEOUT", str(e), client_ip)
            logger.error(f"Telegram API timeout in {f.__name__}: {str(e)}")
            return jsonify({"error": "Превышено время ожидания. Попробуйте позже."}), 503
        except requests.exceptions.RequestException as e:
            log_security_event("TELEGRAM_NETWORK_ERROR", str(e), client_ip)
            logger.error(f"Network error in {f.__name__}: {str(e)}")
            return jsonify({"error": "Ошибка сети при обращении к Telegram API"}), 502
        except Exception as e:
            log_security_event("UNEXPECTED_ERROR", str(e), client_ip)
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            return jsonify({"error": "Внутренняя ошибка сервера"}), 500
    return decorated_function

def validate_and_sanitize_input(f):
    """Декоратор для валидации и очистки входных данных"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = get_remote_address()
        
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                log_security_event("INVALID_JSON", "Empty or invalid JSON", client_ip)
                return jsonify({"error": "Неверный формат данных"}), 400
            
            # Санитизация всех строковых полей
            for key, value in data.items():
                if isinstance(value, str):
                    original_value = value
                    data[key] = sanitize_input(value)
                    
                    # Проверка на подозрительный контент
                    if not validate_no_suspicious_content(original_value):
                        log_security_event("SUSPICIOUS_CONTENT", f"Field: {key}, Content: {original_value[:100]}", client_ip)
                        return jsonify({"error": "Обнаружен подозрительный контент"}), 400
            
            # Валидация email если присутствует
            if 'email' in data and data['email'] and not validate_email(data['email']):
                log_security_event("INVALID_EMAIL", f"Email: {data['email']}", client_ip)
                return jsonify({"error": "Неверный формат email адреса"}), 400
        
        return f(*args, **kwargs)
    return decorated_function

# Telegram API функции
class TelegramAPI:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def get_bot_info(self) -> Dict[str, Any]:
        """Получение информации о боте"""
        response = requests.get(
            f"{self.base_url}/getMe",
            timeout=Config.TELEGRAM_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    
    def send_message(self, text: str) -> Dict[str, Any]:
        """Отправка сообщения"""
        response = requests.post(
            f"{self.base_url}/sendMessage",
            json={"chat_id": self.chat_id, "text": text},
            timeout=Config.TELEGRAM_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    
    def get_updates(self) -> Dict[str, Any]:
        """Получение обновлений"""
        response = requests.get(
            f"{self.base_url}/getUpdates",
            timeout=Config.TELEGRAM_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

# Инициализация Telegram API
telegram_api = TelegramAPI(Config.BOT_TOKEN, Config.CHAT_ID)

# Маршруты
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(app.static_folder, "sitemap.xml", mimetype='application/xml')

@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt", mimetype='text/plain')

@app.route('/api/test', methods=['GET'])
def test_api():
    """Простой тест API"""
    return jsonify({
        "success": True,
        "message": "API работает!",
        "timestamp": datetime.now().isoformat(),
        "telegram_configured": True,
        "limiter_available": True,
        "talisman_available": True
    })

@app.route('/api/test-telegram', methods=['GET'])
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE} per minute")
@handle_telegram_errors
@security_headers
def test_telegram():
    """Тестовый endpoint для проверки работы Telegram бота"""
    client_ip = get_remote_address()
    logger.info(f"Test telegram request from IP: {client_ip}")
    
    # Получение информации о боте
    bot_info = telegram_api.get_bot_info()
    
    # Отправка тестового сообщения
    test_message = f"🔧 Тест соединения с ботом L'ÎLE DE RÊVE\n\nВремя: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nIP: {client_ip}\n\nЕсли вы видите это сообщение, бот работает корректно!"
    send_result = telegram_api.send_message(test_message)
    
    return jsonify({
        "success": True,
        "message": "Тестовое сообщение успешно отправлено!",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/get-chat-id', methods=['GET'])
@limiter.limit("10 per minute")  # Более строгий лимит для этого endpoint
@handle_telegram_errors
@security_headers
def get_chat_id():
    """Получение доступных chat ID (только для администраторов)"""
    client_ip = get_remote_address()
    log_security_event("ADMIN_ENDPOINT_ACCESS", "get-chat-id accessed", client_ip)
    
    # В продакшене этот endpoint должен быть защищен аутентификацией
    if not Config.DEBUG:
        return jsonify({"error": "Доступ запрещен"}), 403
    
    updates_data = telegram_api.get_updates()
    updates = updates_data.get('result', [])
    
    chat_ids = []
    for update in updates[-5:]:  # Только последние 5 обновлений
        if 'message' in update:
            chat = update['message']['chat']
            chat_ids.append({
                'chat_id': str(chat['id']),  # Конвертируем в строку
                'chat_type': chat['type'],
                'title': chat.get('title', '')[:50],  # Ограничиваем длину
                'username': chat.get('username', '')[:30]
            })
    
    return jsonify({
        "success": True,
        "available_chats": chat_ids,
        "total_updates": len(updates),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/send-order-to-telegram', methods=['POST'])
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE} per minute")
@validate_and_sanitize_input
@handle_telegram_errors
@security_headers
def send_order_to_telegram():
    """Отправка данных заказа в Telegram"""
    client_ip = get_remote_address()
    data = request.get_json()
    
    # Валидация обязательных полей для заказа
    required_fields = ['serviceTitle', 'servicePrice', 'duration', 'date', 'name', 'phone']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        log_security_event("ORDER_VALIDATION_ERROR", f"Missing fields: {validation_error}", client_ip)
        return jsonify({"error": validation_error}), 400
    
    # Валидация длины полей
    length_validations = [
        ('name', Config.MAX_NAME_LENGTH),
        ('serviceTitle', 200),  # Ограничение на название услуги
        ('comments', Config.MAX_MESSAGE_LENGTH)
    ]
    
    for field, max_length in length_validations:
        if field in data:
            length_error = validate_field_length(data, field, max_length)
            if length_error:
                log_security_event("ORDER_LENGTH_ERROR", length_error, client_ip)
                return jsonify({"error": length_error}), 400
    
    # Валидация телефона
    phone = data.get('phone', '').strip()
    if not validate_phone(phone):
        log_security_event("ORDER_INVALID_PHONE", f"Phone: {phone}", client_ip)
        return jsonify({
            "error": "Пожалуйста, введите корректный номер телефона (например, +79991112233 или 89991112233)."
        }), 400
    
    # Валидация даты
    date_value = data.get('date', '').strip()
    if not date_value or len(date_value) > 50:
        log_security_event("ORDER_INVALID_DATE", f"Date: {date_value}", client_ip)
        return jsonify({"error": "Пожалуйста, укажите корректную дату начала услуги"}), 400
    
    # Валидация длительности
    try:
        duration = int(data.get('duration', 0))
        if duration <= 0 or duration > 1000:  # Максимум 1000 единиц
            raise ValueError("Invalid duration range")
    except (ValueError, TypeError):
        log_security_event("ORDER_INVALID_DURATION", f"Duration: {data.get('duration')}", client_ip)
        return jsonify({"error": "Длительность должна быть числом от 1 до 1000"}), 400
    
    # Валидация цены
    service_price = str(data.get('servicePrice', '')).strip()
    if len(service_price) > 50:
        log_security_event("ORDER_INVALID_PRICE", f"Price too long: {len(service_price)}", client_ip)
        return jsonify({"error": "Неверный формат цены"}), 400
    
    # Логирование заказа
    logger.info(f"Order from IP: {client_ip}, Service: {data['serviceTitle'][:50]}, Name: {data['name'][:20]}")
    
    # Формирование сообщения о заказе
    comments_text = f"\n💬 Комментарии: {data['comments']}" if data.get('comments') else ""
    email_text = f"\n📧 Email: {data['email']}" if data.get('email') else ""
    
    # Безопасный расчет общей стоимости
    total_text = ""
    try:
        # Извлекаем число из строки цены
        price_clean = re.sub(r'[^\d.,]', '', service_price)
        if price_clean:
            base_price = float(price_clean.replace(',', '.'))
            if 0 < base_price < 10000000:  # Разумные пределы
                total_price = base_price * duration
                total_text = f"\n💰 Общая стоимость: {total_price:,.0f} ₽"
    except (ValueError, AttributeError):
        pass
    
    if not total_text:
        total_text = f"\n💰 Цена за единицу: {service_price}"
    
    telegram_message = f"""🛒 НОВЫЙ ЗАКАЗ с сайта L'ÎLE DE RÊVE

📋 ДЕТАЛИ ЗАКАЗА:
• Услуга: {data['serviceTitle']}
• Цена за единицу: {service_price}
• Длительность: {duration} ед.{total_text}
• Дата начала: {date_value}

👤 ДАННЫЕ КЛИЕНТА:
• Имя: {data['name']}
• Телефон: {phone}{email_text}{comments_text}
🌐 IP: {client_ip}

---
⏰ Заказ оформлен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔔 Требуется подтверждение заказа и связь с клиентом!"""
    
    # Отправка сообщения
    result = telegram_api.send_message(telegram_message)
    
    return jsonify({
        "success": True,
        "message": "Заказ успешно отправлен! Мы свяжемся с вами в ближайшее время для подтверждения.",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/send-to-telegram', methods=['POST'])
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE} per minute")
@validate_and_sanitize_input
@handle_telegram_errors
@security_headers
def send_to_telegram():
    """Отправка сообщения в Telegram"""
    client_ip = get_remote_address()
    data = request.get_json()
    
    # Валидация обязательных полей
    required_fields = ['name', 'message', 'phone']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        log_security_event("VALIDATION_ERROR", f"Missing fields: {validation_error}", client_ip)
        return jsonify({"error": validation_error}), 400
    
    # Валидация длины полей
    length_validations = [
        ('name', Config.MAX_NAME_LENGTH),
        ('message', Config.MAX_MESSAGE_LENGTH)
    ]
    
    for field, max_length in length_validations:
        length_error = validate_field_length(data, field, max_length)
        if length_error:
            log_security_event("LENGTH_VALIDATION_ERROR", length_error, client_ip)
            return jsonify({"error": length_error}), 400
    
    # Валидация телефона
    phone = data.get('phone', '').strip()
    if not validate_phone(phone):
        log_security_event("INVALID_PHONE", f"Phone: {phone}", client_ip)
        return jsonify({
            "error": "Пожалуйста, введите корректный номер телефона (например, +79991112233 или 89991112233)."
        }), 400
    
    # Логирование успешной отправки
    logger.info(f"Contact form submission from IP: {client_ip}, Name: {data['name'][:20]}, Phone: {phone[:15]}")
    
    # Формирование сообщения
    email_text = f"\n📧 Email: {data['email']}" if data.get('email') else ""
    telegram_message = f"""📝 Новое сообщение с сайта L'ÎLE DE RÊVE

👤 Имя: {data['name']}
📱 Телефон: {phone}{email_text}
💬 Сообщение: {data['message']}
🌐 IP: {client_ip}

---
⏰ Отправлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    # Отправка сообщения
    result = telegram_api.send_message(telegram_message)
    
    return jsonify({
        "success": True,
        "message": "Сообщение успешно отправлено!",
        "timestamp": datetime.now().isoformat()
    })

# Обработчики ошибок
@app.errorhandler(404)
def not_found(error):
    client_ip = get_remote_address()
    log_security_event("404_ERROR", f"Path: {request.path}", client_ip)
    return jsonify({"error": "Страница не найдена"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    client_ip = get_remote_address()
    log_security_event("405_ERROR", f"Method: {request.method}, Path: {request.path}", client_ip)
    return jsonify({"error": "Метод не разрешен"}), 405

@app.errorhandler(413)
def too_large(error):
    client_ip = get_remote_address()
    log_security_event("413_ERROR", "Request too large", client_ip)
    return jsonify({"error": "Запрос слишком большой"}), 413

@app.errorhandler(429)
def ratelimit_handler(e):
    client_ip = get_remote_address()
    log_security_event("RATE_LIMIT_EXCEEDED", f"Limit: {e.description}", client_ip)
    return jsonify({"error": "Превышен лимит запросов. Попробуйте позже."}), 429

@app.errorhandler(500)
def internal_error(error):
    client_ip = get_remote_address()
    log_security_event("500_ERROR", str(error), client_ip)
    return jsonify({"error": "Внутренняя ошибка сервера"}), 500

# Middleware для логирования запросов
@app.before_request
def log_request_info():
    client_ip = get_remote_address()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Логирование подозрительных User-Agent
    suspicious_agents = ['bot', 'crawler', 'spider', 'scraper', 'hack', 'scan']
    if any(agent in user_agent.lower() for agent in suspicious_agents):
        log_security_event("SUSPICIOUS_USER_AGENT", f"UA: {user_agent[:200]}", client_ip)
    
    # Логирование больших запросов
    if request.content_length and request.content_length > Config.MAX_CONTENT_LENGTH // 2:
        log_security_event("LARGE_REQUEST", f"Size: {request.content_length}", client_ip)

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# Инициализация при запуске
@app.before_first_request
def startup_security_check():
    """Проверка безопасности при запуске"""
    logger.info("=== SECURITY STARTUP CHECK ===")
    logger.info(f"DEBUG mode: {Config.DEBUG}")
    logger.info(f"Rate limiting: {Config.RATE_LIMIT_PER_MINUTE}/min, {Config.RATE_LIMIT_PER_HOUR}/hour")
    logger.info(f"Max content length: {Config.MAX_CONTENT_LENGTH} bytes")
    logger.info(f"Security headers: Enabled")
    logger.info(f"Input sanitization: Enabled")
    logger.info("=== SECURITY CHECK COMPLETE ===")

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))