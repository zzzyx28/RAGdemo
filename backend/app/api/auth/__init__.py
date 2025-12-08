"""
认证 API 蓝图
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

from . import routes

