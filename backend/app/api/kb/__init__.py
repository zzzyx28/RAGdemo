"""
知识库管理 API 蓝图
"""
from flask import Blueprint

kb_bp = Blueprint('kb', __name__, url_prefix='/api')

from . import routes

