"""
聊天历史管理蓝图
"""
from flask import Blueprint

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

from . import routes  # noqa: E402, F401

