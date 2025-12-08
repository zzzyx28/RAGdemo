from flask import Blueprint

# 创建一个名为 'core' 的蓝图
core_bp = Blueprint('core', __name__, url_prefix='/api')

from . import routes