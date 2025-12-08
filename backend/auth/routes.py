from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models import User  # 导入 User 模型
from .__init__ import auth_bp  # 导入蓝图实例


# -------------------- 认证路由 --------------------

@auth_bp.route('/register', methods=['POST'])
def register():
    # ... (与原 app.py 中注册逻辑相同) ...
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 409

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    # ... (与原 app.py 中登录逻辑相同) ...
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user.username)
    return jsonify(access_token=access_token, username=user.username)


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user, message="Access granted to protected area"), 200