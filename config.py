import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    """Конфигурация приложения"""
    
    # Telegram Bot Configuration
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    CHAT_ID = os.environ.get('CHAT_ID')
    
    # Application Configuration
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # API Configuration
    TELEGRAM_API_TIMEOUT = int(os.environ.get('TELEGRAM_API_TIMEOUT', '10'))
    
    # Validation Configuration
    MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', '1000'))
    MAX_NAME_LENGTH = int(os.environ.get('MAX_NAME_LENGTH', '100'))
    MAX_EMAIL_LENGTH = int(os.environ.get('MAX_EMAIL_LENGTH', '254'))
    MAX_PHONE_LENGTH = int(os.environ.get('MAX_PHONE_LENGTH', '20'))
    
    # Security Configuration
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '60'))
    RATE_LIMIT_PER_HOUR = int(os.environ.get('RATE_LIMIT_PER_HOUR', '300'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '1048576'))  # 1MB
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Strict')
    
    # Content Security Policy
    CSP_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        'style-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        'img-src': "'self' data: https:",
        'font-src': "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        'connect-src': "'self'",
        'frame-ancestors': "'none'",
        'base-uri': "'self'",
        'form-action': "'self'"
    }
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Проверка обязательных настроек"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN не настроен. Установите переменную окружения BOT_TOKEN")
        
        if not cls.CHAT_ID:
            errors.append("CHAT_ID не настроен. Установите переменную окружения CHAT_ID")
            
        if not cls.SECRET_KEY:
            errors.append("SECRET_KEY не настроен. Установите переменную окружения SECRET_KEY")
        elif len(cls.SECRET_KEY) < 32:
            errors.append("SECRET_KEY должен быть не менее 32 символов")
        
        if errors:
            raise ValueError("Ошибки конфигурации:\n" + "\n".join(f"- {error}" for error in errors))
        
        return True

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

# Выбор конфигурации в зависимости от окружения
def get_config():
    """Получение конфигурации в зависимости от окружения"""
    env = os.environ.get('FLASK_ENV', 'production')
    
    if env == 'development':
        return DevelopmentConfig
    else:
        return ProductionConfig 