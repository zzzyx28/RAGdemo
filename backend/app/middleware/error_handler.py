"""
全局错误处理中间件
"""
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended.exceptions import (
    JWTExtendedException,
    NoAuthorizationError,
    InvalidHeaderError,
    WrongTokenError,
    RevokedTokenError,
    FreshTokenRequired,
    CSRFError,
    UserLookupError,
    UserClaimsVerificationError
)
from app.utils.exceptions import APIException
from app.utils.responses import APIResponse


def register_error_handlers(app):
    """
    注册全局错误处理器
    
    Args:
        app: Flask 应用实例
    """
    
    # ========== JWT 认证错误处理 ==========
    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization_error(e):
        """处理缺少认证头错误"""
        current_app.logger.warning(f"JWT Error: {str(e)}")
        return APIResponse.unauthorized("缺少认证令牌，请先登录")
    
    @app.errorhandler(InvalidHeaderError)
    def handle_invalid_header_error(e):
        """处理无效的认证头格式错误"""
        current_app.logger.warning(f"JWT Error: {str(e)}")
        return APIResponse.error(message="认证头格式错误", code=422)
    
    @app.errorhandler(WrongTokenError)
    def handle_wrong_token_error(e):
        """处理错误的Token类型错误"""
        current_app.logger.warning(f"JWT Error: {str(e)}")
        return APIResponse.error(message="Token类型错误", code=422)
    
    @app.errorhandler(RevokedTokenError)
    def handle_revoked_token_error(e):
        """处理已撤销的Token错误"""
        current_app.logger.warning(f"JWT Error: {str(e)}")
        return APIResponse.unauthorized("Token已被撤销，请重新登录")
    
    @app.errorhandler(FreshTokenRequired)
    def handle_fresh_token_required(e):
        """处理需要Fresh Token错误"""
        current_app.logger.warning(f"JWT Error: {str(e)}")
        return APIResponse.error(message="此操作需要重新验证身份", code=422)
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """处理CSRF错误"""
        current_app.logger.warning(f"JWT Error: {str(e)}")
        return APIResponse.error(message="CSRF验证失败", code=403)
    
    @app.errorhandler(UserLookupError)
    def handle_user_lookup_error(e):
        """处理用户查找错误"""
        current_app.logger.warning(f"JWT Error: {str(e)}")
        return APIResponse.unauthorized("用户不存在或已被禁用")
    
    @app.errorhandler(UserClaimsVerificationError)
    def handle_user_claims_verification_error(e):
        """处理用户声明验证错误"""
        current_app.logger.warning(f"JWT Error: {str(e)}")
        return APIResponse.error(message="Token声明验证失败", code=422)
    
    @app.errorhandler(JWTExtendedException)
    def handle_jwt_extended_exception(e):
        """处理其他JWT扩展异常"""
        current_app.logger.warning(f"JWT Error: {str(e)}")
        return APIResponse.unauthorized(f"认证失败: {str(e)}")
    
    # ========== 其他错误处理 ==========
    @app.errorhandler(APIException)
    def handle_api_exception(e: APIException):
        """处理自定义 API 异常"""
        current_app.logger.warning(f"API Exception: {e.message}")
        return APIResponse.error(message=e.message, code=e.code)
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(e: IntegrityError):
        """处理数据库完整性错误"""
        current_app.logger.error(f"Database integrity error: {str(e)}")
        error_str = str(e.orig).lower() if hasattr(e, 'orig') and e.orig else str(e).lower()
        
        if 'unique' in error_str or 'duplicate' in error_str:
            if 'username' in error_str:
                return APIResponse.conflict("用户名已存在")
            elif 'email' in error_str:
                return APIResponse.conflict("邮箱已被注册")
            return APIResponse.conflict("数据冲突")
        
        return APIResponse.error(message="数据库完整性错误", code=409)
    
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(e: SQLAlchemyError):
        """处理 SQLAlchemy 错误"""
        current_app.logger.error(f"Database error: {str(e)}")
        return APIResponse.server_error("数据库操作失败")
    
    @app.errorhandler(400)
    def handle_bad_request(_e):
        """处理 400 错误"""
        return APIResponse.error(message="请求参数错误", code=400)
    
    @app.errorhandler(401)
    def handle_unauthorized(_e):
        """处理 401 错误"""
        return APIResponse.unauthorized()
    
    @app.errorhandler(403)
    def handle_forbidden(_e):
        """处理 403 错误"""
        return APIResponse.forbidden()
    
    @app.errorhandler(404)
    def handle_not_found(_e):
        """处理 404 错误"""
        return APIResponse.not_found()
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        """处理 500 错误"""
        current_app.logger.error(f"Internal server error: {str(e)}")
        return APIResponse.server_error()
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e: Exception):
        """处理未预期的异常"""
        current_app.logger.exception(f"Unhandled exception: {str(e)}")
        return APIResponse.server_error("服务器内部错误")

