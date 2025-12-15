"""
核心功能路由（聊天）
"""
import time
import json
from flask import request, Response, current_app, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils.responses import APIResponse
from app.extensions import db
from app.models import Conversation, Message
from . import core_bp


def non_rag_chat_generator(_prompt, conversation_id=None, user_message_id=None):
    """非 RAG 模式流式生成器（逐字符输出）"""
    # 首先发送 conversation_id（如果存在）
    if conversation_id:
        yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation_id})}\n\n"
    
    response_text = "测试回复：非RAG模式下的回复"
    full_content = ""
    # 逐字符 yield，实现打字机效果
    for char in response_text:
        full_content += char
        yield f"data: {json.dumps({'type': 'content', 'content': char})}\n\n"
        time.sleep(0.05)  # 保持和 RAG 一致的打字机间隔
    # 输出结束标识
    yield "data: [DONE]\n\n"
    
    # 保存助手消息到数据库（在请求上下文中执行）
    if conversation_id and user_message_id:
        try:
            assistant_message = Message(
                conversation_id=conversation_id,
                role='assistant',
                content=full_content
            )
            db.session.add(assistant_message)
            
            # 更新对话的更新时间
            conversation = Conversation.query.get(conversation_id)
            if conversation:
                from datetime import datetime
                conversation.updated_at = datetime.utcnow()
            
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"保存助手消息失败: {str(e)}")
            db.session.rollback()


def rag_chat_generator(_prompt, conversation_id=None, user_message_id=None):
    """
    模拟 RAG 处理逻辑
    这是一个生成器，它模拟了 RAG 的三个阶段：
    1. Embedding & Search (检索)
    2. Prompt Construction (构建上下文)
    3. Generation (生成回答)
    """
    # 首先发送 conversation_id（如果存在）
    if conversation_id:
        yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation_id})}\n\n"
    
    # --- 阶段 1: 模拟检索过程 ---
    time.sleep(1.5)  # 模拟去向量数据库查询的时间
    
    # 模拟检索到的文档片段
    mock_sources = []
    
    # 发送一个特殊事件告诉前端：检索结束，并带上引用源
    yield f"data: {json.dumps({'type': 'searching_end', 'sources': mock_sources})}\n\n"
    
    # --- 阶段 2: 模拟 LLM 基于文档回答 ---
    response_text = "测试回复：xxxxx"
    full_content = ""
    
    for char in response_text:
        full_content += char
        yield f"data: {json.dumps({'type': 'content', 'content': char})}\n\n"
        time.sleep(0.05)  # 打字机效果
    
    yield "data: [DONE]\n\n"
    
    # 保存助手消息到数据库（在请求上下文中执行）
    if conversation_id and user_message_id:
        try:
            assistant_message = Message(
                conversation_id=conversation_id,
                role='assistant',
                content=full_content,
                sources=json.dumps(mock_sources) if mock_sources else None
            )
            db.session.add(assistant_message)
            
            # 更新对话的更新时间
            conversation = Conversation.query.get(conversation_id)
            if conversation:
                from datetime import datetime
                conversation.updated_at = datetime.utcnow()
            
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"保存助手消息失败: {str(e)}")
            db.session.rollback()


@core_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """聊天接口（流式响应）"""
    if not request.is_json:
        return APIResponse.error(message="Content-Type must be application/json", code=400)
    
    data = request.get_json()
    if not data:
        return APIResponse.error(message="Invalid JSON data", code=400)
    
    prompt = data.get('message', '')
    use_rag = data.get('use_rag', False)
    conversation_id = data.get('conversation_id')  # 可选，如果不存在则创建新对话
    
    if not prompt:
        return APIResponse.error(message="No prompt provided", code=400)
    
    current_app.logger.info(f"收到聊天请求: {prompt[:50]}..., 是否使用RAG: {use_rag}, 对话ID: {conversation_id}")
    
    try:
        user_id = get_jwt_identity()
        user_message_id = None
        
        # 处理对话和用户消息
        conversation = None
        
        # 重要：只有当 conversation_id 存在且有效时才使用现有对话
        if conversation_id is not None and conversation_id != 0:
            # 验证对话属于当前用户
            conversation = Conversation.query.filter_by(
                id=conversation_id,
                user_id=user_id
            ).first()
            
            if conversation:
                current_app.logger.info(f"使用现有对话: conversation_id={conversation_id}, 标题={conversation.title}")
            else:
                current_app.logger.warning(f"对话不存在或无权限: conversation_id={conversation_id}, user_id={user_id}, 将创建新对话")
        
        # 如果没有有效对话，创建新对话
        if not conversation:
            # 创建新对话（只有在没有 conversation_id 时才创建）
            # 使用第一条消息的前50个字符作为标题，如果超过50字符则截断
            title = prompt.strip()[:50] if len(prompt.strip()) > 50 else prompt.strip()
            if not title:
                title = "新对话"
            conversation = Conversation(
                user_id=user_id,
                title=title
            )
            db.session.add(conversation)
            db.session.flush()  # 获取 conversation.id
            conversation_id = conversation.id
            current_app.logger.info(f"创建新对话: ID={conversation_id}, 标题={title}")
        
        # 保存用户消息
        user_message = Message(
            conversation_id=conversation_id,
            role='user',
            content=prompt
        )
        db.session.add(user_message)
        db.session.flush()  # 获取 user_message.id
        user_message_id = user_message.id
        
        # 更新对话的更新时间
        from datetime import datetime
        conversation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # 生成流式响应（使用 stream_with_context 保持请求上下文）
        # 在响应头中返回 conversation_id，方便前端更新
        headers = {
            'X-Conversation-Id': str(conversation_id)
        }
        
        if use_rag:
            return Response(
                stream_with_context(rag_chat_generator(prompt, conversation_id, user_message_id)),
                mimetype='text/event-stream',
                headers=headers
            )
        else:
            return Response(
                stream_with_context(non_rag_chat_generator(prompt, conversation_id, user_message_id)),
                mimetype='text/event-stream',
                headers=headers
            )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"处理聊天请求时出错: {str(e)}")
        return APIResponse.server_error("处理聊天请求失败")

