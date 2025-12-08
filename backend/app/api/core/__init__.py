"""
核心功能 API 蓝图
"""
from flask import Blueprint

core_bp = Blueprint('core', __name__, url_prefix='/api')

from . import routes

