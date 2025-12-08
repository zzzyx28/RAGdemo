from flask import Blueprint

# 创建一个名为 'auth' 的蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# 导入路由文件，确保路由被注册
from . import routes