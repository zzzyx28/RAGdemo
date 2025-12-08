"""
输入验证工具
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    验证密码强度
    
    Args:
        password: 密码
        
    Returns:
        (is_valid, error_message) 元组
    """
    if len(password) < 8:
        return False, "密码长度至少8位"
    
    if len(password) > 128:
        return False, "密码长度不能超过128位"
    
    # 已取消：密码必须包含字母的要求
    # if not re.search(r'[A-Za-z]', password):
    #     return False, "密码必须包含至少一个字母"
    
    # 已取消：密码必须包含数字的要求
    # if not re.search(r'[0-9]', password):
    #     return False, "密码必须包含至少一个数字"
    
    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    验证用户名格式
    
    Args:
        username: 用户名
        
    Returns:
        (is_valid, error_message) 元组
    """
    if not username or not username.strip():
        return False, "用户名不能为空"
    
    if len(username) < 3:
        return False, "用户名长度至少3位"
    
    if len(username) > 30:
        return False, "用户名长度不能超过30位"
    
    # 只允许字母、数字、下划线和连字符
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "用户名只能包含字母、数字、下划线和连字符"
    
    return True, None


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    清理输入文本
    
    Args:
        text: 输入文本
        max_length: 最大长度限制
        
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    
    # 去除首尾空白
    text = text.strip()
    
    # 限制长度
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

