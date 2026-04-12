import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY         = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY     = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    SQLALCHEMY_DATABASE_URI        = os.getenv("DATABASE_URL", "sqlite:///ppa.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL             = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL     = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Flask-Caching — uses Redis, separate DB index (db=1) to not mix with Celery (db=0)
    CACHE_TYPE              = "RedisCache"
    CACHE_REDIS_URL         = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/1")
    CACHE_DEFAULT_TIMEOUT   = 300   # 5 minutes default expiry

    # MailHog — local fake email server (view at http://localhost:8025)
    MAIL_SERVER        = "localhost"
    MAIL_PORT          = 1025
    MAIL_USE_TLS       = False
    MAIL_USE_SSL       = False
    MAIL_USERNAME      = None
    MAIL_PASSWORD      = None
    MAIL_DEFAULT_SENDER = "noreply@ppa.edu"
    ADMIN_EMAIL        = os.getenv("ADMIN_EMAIL", "admin@institute.edu")

    UPLOAD_FOLDER       = os.path.join(os.path.dirname(__file__), "uploads")
    MAX_CONTENT_LENGTH  = 5 * 1024 * 1024  # 5 MB

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}
