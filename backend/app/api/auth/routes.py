"""
认证路由
"""
from flask import request, current_app
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity
)
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import User
from app.utils.responses import APIResponse
from app.utils.validators import validate_email, validate_password, validate_username, sanitize_input
from . import auth_bp


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.get_json()
    if not data:
        return APIResponse.error(message="无效的JSON数据", code=400)
    
    # 验证必要字段
    required_fields = ['username', 'email', 'password']
    if not all(k in data for k in required_fields):
        return APIResponse.error(
            message="缺少必要字段",
            errors={"required": required_fields}
        )
    
    # 输入清理和验证
    username = sanitize_input(data['username'])
    email = sanitize_input(data['email']).lower()
    password = data['password']
    full_name = sanitize_input(data.get('full_name', ''))
    
    # 验证用户名
    is_valid, error_msg = validate_username(username)
    if not is_valid:
        return APIResponse.error(message=error_msg, code=400)
    
    # 验证邮箱
    if not validate_email(email):
        return APIResponse.error(message="邮箱格式不正确", code=400)
    
    # 验证密码
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return APIResponse.error(message=error_msg, code=400)
    
    try:
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            return APIResponse.conflict("用户名已存在")
        if User.query.filter_by(email=email).first():
            return APIResponse.conflict("邮箱已被注册")
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            full_name=full_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        current_app.logger.info(f"新用户注册: {username}")
        return APIResponse.success(
            data={"user": user.to_dict()},
            message="注册成功",
            code=201
        )
        
    except ValueError as e:
        db.session.rollback()
        return APIResponse.error(message=str(e), code=400)
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"注册时数据库错误: {str(e)}")
        raise  # 让全局错误处理器处理


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    if not data:
        return APIResponse.error(message="无效的请求数据", code=400)
    
    username = sanitize_input(data.get('username', ''))
    password = data.get('password', '')
    
    if not username or not password:
        return APIResponse.error(message="用户名和密码不能为空", code=400)
    
    try:
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            current_app.logger.warning(f"登录失败: {username}")
            return APIResponse.unauthorized("用户名或密码错误")
        
        if not user.is_active:
            return APIResponse.forbidden("账号已被禁用")
        
        # 创建 Token
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24)
        )
        
        current_app.logger.info(f"用户登录: {username}")
        return APIResponse.success(
            data={
                "access_token": access_token,
                "username": user.username,
                "user": user.to_dict()
            },
            message="登录成功"
        )
        
    except SQLAlchemyError as e:
        current_app.logger.error(f"登录时数据库错误: {str(e)}")
        raise  # 让全局错误处理器处理


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """获取用户个人资料"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return APIResponse.unauthorized("无效的认证信息")
        
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            return APIResponse.error(message="无效的用户ID格式", code=400)
        
        user = User.query.get(user_id_int)
        if not user:
            return APIResponse.not_found("用户不存在")
        
        if not user.is_active:
            return APIResponse.forbidden("账号已被禁用")
        
        return APIResponse.success(
            data={"user": user.to_dict()},
            message="获取成功"
        )
        
    except SQLAlchemyError as e:
        current_app.logger.error(f"获取用户资料时数据库错误: {str(e)}")
        raise  # 让全局错误处理器处理

