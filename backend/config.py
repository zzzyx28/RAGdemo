import datetime
class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///enterprise_ai.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT 配置
    JWT_SECRET_KEY = "super-secret-key-replace-me-in-prod"
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=24)