"""
统一 API 响应格式工具
"""
from flask import jsonify
from typing import Any, Optional, Dict


class APIResponse:
    """统一 API 响应格式"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        code: int = 200
    ) -> tuple:
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            code: HTTP 状态码
            
        Returns:
            (response, status_code) 元组
        """
        response = {
            "code": code,
            "message": message,
            "data": data
        }
        return jsonify(response), code
    
    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = 400,
        errors: Optional[Dict] = None
    ) -> tuple:
        """
        错误响应
        
        Args:
            message: 错误消息
            code: HTTP 状态码
            errors: 详细错误信息（可选）
            
        Returns:
            (response, status_code) 元组
        """
        response = {
            "code": code,
            "message": message
        }
        if errors:
            response["errors"] = errors
        return jsonify(response), code
    
    @staticmethod
    def unauthorized(message: str = "未授权访问") -> tuple:
        """401 未授权响应"""
        return APIResponse.error(message=message, code=401)
    
    @staticmethod
    def forbidden(message: str = "禁止访问") -> tuple:
        """403 禁止访问响应"""
        return APIResponse.error(message=message, code=403)
    
    @staticmethod
    def not_found(message: str = "资源不存在") -> tuple:
        """404 未找到响应"""
        return APIResponse.error(message=message, code=404)
    
    @staticmethod
    def conflict(message: str = "资源冲突") -> tuple:
        """409 冲突响应"""
        return APIResponse.error(message=message, code=409)
    
    @staticmethod
    def server_error(message: str = "服务器内部错误") -> tuple:
        """500 服务器错误响应"""
        return APIResponse.error(message=message, code=500)

