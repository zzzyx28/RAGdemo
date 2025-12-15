"""
聊天历史管理路由
"""
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils.responses import APIResponse
from app.extensions import db
from app.models import Conversation, Message, User
from . import chat_bp


@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """获取当前用户的所有对话列表"""
    try:
        user_id = get_jwt_identity()
        
        # 获取对话列表，按更新时间倒序
        conversations = Conversation.query.filter_by(user_id=user_id)\
            .order_by(Conversation.updated_at.desc())\
            .all()
        
        return APIResponse.success(
            data=[conv.to_dict() for conv in conversations],
            message="获取对话列表成功"
        )
    except Exception as e:
        current_app.logger.error(f"获取对话列表失败: {str(e)}")
        return APIResponse.server_error("获取对话列表失败")


@chat_bp.route('/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    """创建新对话"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        title = data.get('title', '新对话')
        
        # 创建新对话
        conversation = Conversation(
            user_id=user_id,
            title=title[:200]  # 限制标题长度
        )
        db.session.add(conversation)
        db.session.commit()
        
        return APIResponse.success(
            data=conversation.to_dict(),
            message="创建对话成功"
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建对话失败: {str(e)}")
        return APIResponse.server_error("创建对话失败")


@chat_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    """获取单个对话及其消息"""
    try:
        user_id = get_jwt_identity()
        
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            return APIResponse.error(message="对话不存在", code=404)
        
        return APIResponse.success(
            data=conversation.to_dict(include_messages=True),
            message="获取对话成功"
        )
    except Exception as e:
        current_app.logger.error(f"获取对话失败: {str(e)}")
        return APIResponse.server_error("获取对话失败")


@chat_bp.route('/conversations/<int:conversation_id>', methods=['PUT'])
@jwt_required()
def update_conversation(conversation_id):
    """更新对话标题"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            return APIResponse.error(message="对话不存在", code=404)
        
        if 'title' in data:
            conversation.title = data['title'][:200]
            db.session.commit()
        
        return APIResponse.success(
            data=conversation.to_dict(),
            message="更新对话成功"
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新对话失败: {str(e)}")
        return APIResponse.server_error("更新对话失败")


@chat_bp.route('/conversations/<int:conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conversation_id):
    """删除对话（级联删除所有消息）"""
    try:
        user_id = get_jwt_identity()
        
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            return APIResponse.error(message="对话不存在", code=404)
        
        db.session.delete(conversation)
        db.session.commit()
        
        return APIResponse.success(message="删除对话成功")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除对话失败: {str(e)}")
        return APIResponse.server_error("删除对话失败")


@chat_bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
@jwt_required()
def add_message(conversation_id):
    """向对话中添加消息"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # 验证对话属于当前用户
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            return APIResponse.error(message="对话不存在", code=404)
        
        role = data.get('role')
        content = data.get('content', '')
        sources = data.get('sources')
        
        if role not in ['user', 'assistant']:
            return APIResponse.error(message="角色必须是 'user' 或 'assistant'", code=400)
        
        # 将 sources 转换为 JSON 字符串
        import json
        sources_json = None
        if sources:
            sources_json = json.dumps(sources)
        
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources_json
        )
        
        db.session.add(message)
        
        # 更新对话的更新时间
        from datetime import datetime
        conversation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return APIResponse.success(
            data=message.to_dict(),
            message="添加消息成功"
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加消息失败: {str(e)}")
        return APIResponse.server_error("添加消息失败")

