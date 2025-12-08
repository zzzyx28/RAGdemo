import time
import json
from flask import request, Response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity # 需要 JWT 装饰器和身份获取

from .__init__ import core_bp # 导入蓝图实例


def non_rag_chat_generator(prompt):
    """非 RAG 模式流式生成器（逐字符输出）"""
    response_text = f"测试回复：非RAG模式下的回复"
    # 逐字符 yield，实现打字机效果
    for char in response_text:
        yield f"data: {json.dumps({'type': 'content', 'content': char})}\n\n"
        time.sleep(0.05)  # 保持和 RAG 一致的打字机间隔
    # 输出结束标识
    yield f"data: [DONE]\n\n"


# 模拟 RAG 处理逻辑
def rag_chat_generator(prompt):
    """
    这是一个生成器，它模拟了 RAG 的三个阶段：
    1. Embedding & Search (检索)
    2. Prompt Construction (构建上下文)
    3. Generation (生成回答)
    """

    # --- 阶段 1: 模拟检索过程 ---
    # 在前端，这会显示一个转圈圈的状态
    time.sleep(1.5)  # 模拟去向量数据库查询的时间

    # 模拟检索到的文档片段
    mock_sources = [

    ]

    # 发送一个特殊事件告诉前端：检索结束，并带上引用源
    yield f"data: {json.dumps({'type': 'searching_end', 'sources': mock_sources})}\n\n"

    # --- 阶段 2: 模拟 LLM 基于文档回答 ---
    response_text = f"测试回复：xxxxx"

    for char in response_text:
        yield f"data: {json.dumps({'type': 'content', 'content': char})}\n\n"
        time.sleep(0.05)  # 打字机效果

    yield f"data: [DONE]\n\n"


@core_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    print("收到/api/chat的POST请求")
    data = request.json
    prompt = data.get('message', '')
    use_rag = data.get('use_rag', False)

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    print(f"收到请求: {prompt}, 是否使用RAG: {use_rag}")
    if use_rag:
        # 实际项目中，这里会调用 core/rag_engine.py 的逻辑
        return Response(rag_chat_generator(prompt), mimetype='text/event-stream')
    else:
        # 模拟 LLM 回复
        return Response(non_rag_chat_generator(prompt), mimetype='text/event-stream')

