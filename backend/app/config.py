"""
应用配置
支持从环境变量读取配置
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """基础配置类"""
    
    # 基础路径
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')
    
    # 确保必要的目录存在
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(LOGS_FOLDER, exist_ok=True)
    
    # 数据库配置
    # 使用相对路径，Flask-SQLAlchemy 会自动基于 instance_path 处理
    # 注意：只需要数据库文件名，不要包含 'instance/' 前缀
    # 如果环境变量包含 'instance/'，需要移除它
    env_db_url = os.getenv('DATABASE_URL', '')
    if env_db_url and env_db_url.startswith('sqlite:///'):
        # 移除可能的 'instance/' 前缀，避免路径重复
        db_path = env_db_url.replace('sqlite:///', '')
        if db_path.startswith('instance/'):
            db_path = db_path.replace('instance/', '', 1)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}' if db_path else 'sqlite:///demo.db'
    else:
        SQLALCHEMY_DATABASE_URI = env_db_url if env_db_url else 'sqlite:///demo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据库连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'check_same_thread': False,  # SQLite 多线程支持（Flask 需要）
            'timeout': 20,  # 连接超时时间（秒）
            'isolation_level': None,  # 自动提交模式（可选）
        },
        'pool_pre_ping': True,  # 连接前检查连接是否有效
        'echo': False,  # 是否打印 SQL 语句（调试用）
    }
    
    # JWT 配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-prod')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', '24'))
    )
    
    # CORS 配置
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS',
        'http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173'
    ).split(',')
    
    # 文件上传配置
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', '10485760'))  # 10MB
    ALLOWED_EXTENSIONS = set(
        os.getenv('ALLOWED_EXTENSIONS', 'txt,pdf,md,doc,docx,csv').split(',')
    )
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(LOGS_FOLDER, 'app.log')
    
    # ChromaDB 配置
    CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', os.path.join(INSTANCE_PATH, 'chroma_db'))


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境必须从环境变量读取密钥
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY must be set in production environment")


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

