"""
核心功能路由（聊天）
"""
import time
import json
from flask import request, Response, current_app
from flask_jwt_extended import jwt_required

from app.utils.responses import APIResponse
from . import core_bp


def non_rag_chat_generator(_prompt):
    """非 RAG 模式流式生成器（逐字符输出）"""
    response_text = "测试回复：非RAG模式下的回复"
    # 逐字符 yield，实现打字机效果
    for char in response_text:
        yield f"data: {json.dumps({'type': 'content', 'content': char})}\n\n"
        time.sleep(0.05)  # 保持和 RAG 一致的打字机间隔
    # 输出结束标识
    yield "data: [DONE]\n\n"


def rag_chat_generator(_prompt):
    """
    模拟 RAG 处理逻辑
    这是一个生成器，它模拟了 RAG 的三个阶段：
    1. Embedding & Search (检索)
    2. Prompt Construction (构建上下文)
    3. Generation (生成回答)
    """
    # --- 阶段 1: 模拟检索过程 ---
    time.sleep(1.5)  # 模拟去向量数据库查询的时间
    
    # 模拟检索到的文档片段
    mock_sources = []
    
    # 发送一个特殊事件告诉前端：检索结束，并带上引用源
    yield f"data: {json.dumps({'type': 'searching_end', 'sources': mock_sources})}\n\n"
    
    # --- 阶段 2: 模拟 LLM 基于文档回答 ---
    response_text = "测试回复：xxxxx"
    
    for char in response_text:
        yield f"data: {json.dumps({'type': 'content', 'content': char})}\n\n"
        time.sleep(0.05)  # 打字机效果
    
    yield "data: [DONE]\n\n"


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
    
    if not prompt:
        return APIResponse.error(message="No prompt provided", code=400)
    
    current_app.logger.info(f"收到聊天请求: {prompt[:50]}..., 是否使用RAG: {use_rag}")
    
    try:
        if use_rag:
            return Response(rag_chat_generator(prompt), mimetype='text/event-stream')
        else:
            return Response(non_rag_chat_generator(prompt), mimetype='text/event-stream')
    except Exception as e:
        current_app.logger.error(f"处理聊天请求时出错: {str(e)}")
        return APIResponse.server_error("处理聊天请求失败")

