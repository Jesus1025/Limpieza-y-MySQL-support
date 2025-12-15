import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'teknetau-dev-key-2025'
    DATABASE_PATH = 'database/teknetau.db'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Configuración para producción
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}