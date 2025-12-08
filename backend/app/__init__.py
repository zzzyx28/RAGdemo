"""
Flask 应用工厂
"""
from flask import Flask
from flask_cors import CORS
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import config
from app.extensions import db, jwt
from app.middleware.error_handler import register_error_handlers

# 导入蓝图
from app.api.auth import auth_bp
from app.api.core import core_bp
from app.api.kb import kb_bp

# 导入模型（确保 SQLAlchemy 能创建表）
from app.models import User  # noqa: F401


def create_app(config_name='default'):
    """
    应用工厂函数
    
    Args:
        config_name: 配置名称 ('development', 'production', 'testing', 'default')
        
    Returns:
        Flask 应用实例
    """
    # 加载配置
    config_class = config.get(config_name, config['default'])
    
    # 创建 Flask 应用，设置 instance_path
    app = Flask(__name__, instance_path=config_class.INSTANCE_PATH)
    app.config.from_object(config_class)
    
    # CORS 配置
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(core_bp)
    app.register_blueprint(kb_bp)
    
    # 初始化数据库
    init_database(app)
    
    # 配置日志
    configure_logging(app)
    
    return app


def init_database(app):
    """
    初始化数据库
    
    Args:
        app: Flask 应用实例
    """
    import os
    
    with app.app_context():
        try:
            # 确保 instance_path 目录存在且有写入权限
            instance_dir = app.instance_path
            if not os.path.exists(instance_dir):
                os.makedirs(instance_dir, exist_ok=True)
            
            if not os.access(instance_dir, os.W_OK):
                raise PermissionError(f"Cannot write to instance directory: {instance_dir}")
            
            # 创建数据库表（Flask-SQLAlchemy 会自动处理路径）
            db.create_all()
            
            # 测试数据库连接
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            
            app.logger.info("Database initialized successfully.")
            
        except SQLAlchemyError as e:
            app.logger.error(f"Database initialization error: {str(e)}")
            raise
        except (ValueError, TypeError, AttributeError, PermissionError) as e:
            app.logger.error(f"Database configuration error: {str(e)}")
            raise


def configure_logging(app):
    """
    配置日志
    
    Args:
        app: Flask 应用实例
    """
    import logging
    from logging.handlers import RotatingFileHandler
    
    if not app.debug:
        # 生产环境：文件日志
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    app.logger.info('Application startup')

