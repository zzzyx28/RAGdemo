from flask import Blueprint

# 创建一个名为 'kb' 的蓝图
kb_bp = Blueprint('kb', __name__, url_prefix='/api')

from . import routes