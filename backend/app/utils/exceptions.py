"""
自定义异常类
"""


class APIException(Exception):
    """API 基础异常类"""
    
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(APIException):
    """验证错误"""
    
    def __init__(self, message: str = "验证失败"):
        super().__init__(message, code=400)


class AuthenticationError(APIException):
    """认证错误"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, code=401)


class AuthorizationError(APIException):
    """授权错误"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, code=403)


class NotFoundError(APIException):
    """资源未找到错误"""
    
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, code=404)


class ConflictError(APIException):
    """资源冲突错误"""
    
    def __init__(self, message: str = "资源冲突"):
        super().__init__(message, code=409)

