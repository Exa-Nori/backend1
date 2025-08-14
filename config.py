import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    """Конфигурация приложения"""
    
    # Telegram Bot Configuration
    BOT_TOKEN = os.environ.get('BOT_TOKEN', "7585621279:AAFLcwzw-lrh5PCHvgGZqZ6lG-TIPlwXZZo")
    CHAT_ID = os.environ.get('CHAT_ID', "8191889121")
    
    # Application Configuration
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # API Configuration
    TELEGRAM_API_TIMEOUT = int(os.environ.get('TELEGRAM_API_TIMEOUT', '10'))
    
    # Validation Configuration
    MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', '1000'))
    MAX_NAME_LENGTH = int(os.environ.get('MAX_NAME_LENGTH', '100'))
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Проверка обязательных настроек"""
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "your_telegram_bot_token_here":
            raise ValueError("BOT_TOKEN не настроен. Установите переменную окружения BOT_TOKEN")
        
        if not cls.CHAT_ID or cls.CHAT_ID == "your_chat_id_here":
            raise ValueError("CHAT_ID не настроен. Установите переменную окружения CHAT_ID")
        
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
