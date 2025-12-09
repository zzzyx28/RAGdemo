"""
应用配置
支持从环境变量读取配置，优先使用环境变量，否则使用默认值
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
# 注意：.env 文件是可选的，所有配置都有合理的默认值
load_dotenv()


def get_env_bool(key: str, default: bool = False) -> bool:
    """从环境变量读取布尔值"""
    value = os.getenv(key, '').lower()
    return value in ('true', '1', 'yes', 'on') if value else default


def get_env_int(key: str, default: int) -> int:
    """从环境变量读取整数值"""
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


def get_env_list(key: str, default: list, separator: str = ',') -> list:
    """从环境变量读取列表（用分隔符分隔）"""
    value = os.getenv(key, '')
    return [item.strip() for item in value.split(separator) if item.strip()] if value else default


class Config:
    """基础配置类
    
    所有配置都支持从环境变量读取，如果没有设置环境变量则使用默认值。
    开发环境可以直接使用默认值，生产环境建议通过 .env 文件或环境变量设置。
    """
    
    # ========== 基础路径配置 ==========
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')
    
    # 确保必要的目录存在
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(LOGS_FOLDER, exist_ok=True)
    
    # ========== 数据库配置 ==========
    # 默认使用 SQLite，可通过 DATABASE_URL 环境变量覆盖
    # SQLite: sqlite:///demo.db
    # PostgreSQL: postgresql://user:password@localhost/dbname
    # MySQL: mysql://user:password@localhost/dbname
    _db_url = os.getenv('DATABASE_URL', '')
    if _db_url:
        # 处理 SQLite 路径，移除可能的 'instance/' 前缀
        if _db_url.startswith('sqlite:///'):
            db_path = _db_url.replace('sqlite:///', '')
            if db_path.startswith('instance/'):
                db_path = db_path.replace('instance/', '', 1)
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        else:
            SQLALCHEMY_DATABASE_URI = _db_url
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///demo.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据库连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'check_same_thread': False,  # SQLite 多线程支持
            'timeout': 20,
            'isolation_level': None,
        },
        'pool_pre_ping': True,
        'echo': False,  # 设置为 True 可打印 SQL 语句（调试用）
    }
    
    # ========== JWT 认证配置 ==========
    # 开发环境使用默认密钥，生产环境必须通过环境变量设置强密钥
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-prod')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=get_env_int('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 24)
    )
    # Refresh Token 过期时间（默认30天）
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=get_env_int('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30)
    )
    # Token 位置：从请求头中获取
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # ========== CORS 配置 ==========
    # 开发环境默认允许 localhost，生产环境需要设置实际域名
    CORS_ORIGINS = get_env_list(
        'CORS_ORIGINS',
        ['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:5173']
    )
    
    # ========== 文件上传配置 ==========
    MAX_UPLOAD_SIZE = get_env_int('MAX_UPLOAD_SIZE', 10485760)  # 默认 10MB
    ALLOWED_EXTENSIONS = set(
        get_env_list('ALLOWED_EXTENSIONS', ['txt', 'pdf', 'md', 'doc', 'docx', 'csv'])
    )
    
    # ========== 日志配置 ==========
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(LOGS_FOLDER, 'app.log')
    
    # ========== ChromaDB 配置 ==========
    CHROMA_DB_PATH = os.getenv(
        'CHROMA_DB_PATH',
        os.path.join(INSTANCE_PATH, 'chroma_db')
    )


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置
    
    生产环境要求：
    1. JWT_SECRET_KEY 必须通过环境变量设置（不能使用默认值）
    2. 建议设置 DATABASE_URL 使用生产数据库
    3. CORS_ORIGINS 应设置为实际的前端域名
    
    注意：如果 JWT_SECRET_KEY 未设置或使用默认值，应用启动时会抛出异常
    """
    DEBUG = False
    TESTING = False
    
    # 生产环境必须从环境变量读取密钥，不允许使用默认值
    # 在类加载时检查，如果未设置则抛出异常
    _jwt_secret = os.getenv('JWT_SECRET_KEY')
    if not _jwt_secret or _jwt_secret == 'dev-secret-key-change-in-prod':
        raise ValueError(
            "JWT_SECRET_KEY must be set in production environment. "
            "Please set it via environment variable or .env file."
        )
    JWT_SECRET_KEY = _jwt_secret


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

