"""
Flask 扩展实例
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# 数据库实例
db = SQLAlchemy()

# JWT 认证实例
jwt = JWTManager()

