# backend/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# 数据库实例
db = SQLAlchemy()

# JWT 认证实例
jwt = JWTManager()

# ⚠️ 注意：这里只是创建了实例，但没有传入 Flask 应用实例 `app`