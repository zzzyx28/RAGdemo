"""
全局错误处理中间件
"""
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.utils.exceptions import APIException
from app.utils.responses import APIResponse


def register_error_handlers(app):
    """
    注册全局错误处理器
    
    Args:
        app: Flask 应用实例
    """
    
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

