from flask import Flask
# 导入所有需要用到的蓝图和模型
from auth import auth_bp
from backend.core import core_bp
from backend.kb_management import kb_bp
from models import User  # 导入 User 模型，确保 db.create_all() 知道有哪些表
from extensions import db, jwt  # 导入扩展实例
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. 初始化并绑定扩展 (核心步骤)
    db.init_app(app)
    jwt.init_app(app)

    # 2. 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(kb_bp)
    app.register_blueprint(core_bp)

    return app

# ----------------- 启动应用 -----------------

app = create_app()

# 确保在应用上下文中使用 db.create_all()
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)