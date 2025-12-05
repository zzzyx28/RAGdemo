import os
import time
import json
# 引入安全文件名处理工具
from werkzeug.utils import secure_filename 
from flask import Flask, request, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 限制最大上传 16MB

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'doc', 'docx', 'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------------------------------------------------------
# 新增：获取知识库信息接口 (真实读取文件夹和向量库状态)
# ----------------------------------------------------------------
@app.route('/api/kb-info', methods=['GET'])
def get_kb_info():
    # 1. 获取真实文件列表
    files = []
    if os.path.exists(UPLOAD_FOLDER):
        # 遍历 uploads 文件夹
        for f in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, f)
            if os.path.isfile(file_path) and not f.startswith('.'):
                # 获取文件大小 (KB)
                size_kb = os.path.getsize(file_path) / 1024
                files.append({
                    "name": f,
                    "size": f"{size_kb:.1f} KB",
                    "type": f.split('.')[-1].lower()
                })
    
    # 2. 获取真实的向量数量 (这里模拟查询 ChromaDB)
    # 实际项目中，代码应该是：
    # client = chromadb.PersistentClient(path="./storage")
    # collection = client.get_collection("my_knowledge_base")
    # vector_count = collection.count()
    
    # 暂时用文件数量模拟一个“估算”的向量数，或者你可以返回真实值 0
    # 假设每个文件平均切分成了 52 个片段 (这里仅做演示，请替换为你的真实DB查询)
    vector_count = len(files) * 52 
    
    return jsonify({
        "file_count": len(files),
        "vector_count": vector_count, 
        "files": files
    })


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
    time.sleep(1.5) # 模拟去向量数据库查询的时间
    
    # 模拟检索到的文档片段
    mock_sources = [

    ]
    
    # 发送一个特殊事件告诉前端：检索结束，并带上引用源
    yield f"data: {json.dumps({'type': 'searching_end', 'sources': mock_sources})}\n\n"

    # --- 阶段 2: 模拟 LLM 基于文档回答 ---
    response_text = f"测试回复：xxxxx"
    
    for char in response_text:
        yield f"data: {json.dumps({'type': 'content', 'content': char})}\n\n"
        time.sleep(0.05) # 打字机效果
    
    yield f"data: [DONE]\n\n"


@app.route('/api/chat', methods=['POST'])
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


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('file') # 支持多文件上传
    saved_files = []
    errors = []

    for file in files:
        if file.filename == '':
            continue
            
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 保存文件
            file.save(file_path)
            
            # TODO: 这里应该触发异步任务：
            # 1. 读取文件内容 (Loader)
            # 2. 文本切片 (Splitter)
            # 3. 向量化并存入 ChromaDB (Vector Store)
            # print(f"Triggering background indexing for {filename}...")
            
            saved_files.append(filename)
        else:
            errors.append(f"File {file.filename} not allowed")

    if not saved_files and errors:
        return jsonify({'error': 'Upload failed', 'details': errors}), 400

    return jsonify({
        'message': f'Successfully uploaded {len(saved_files)} files', 
        'files': saved_files,
        'errors': errors
    })

# ----------------------------------------------------------------
# 新增：删除文件接口
# ----------------------------------------------------------------
@app.route('/api/delete', methods=['POST'])
def delete_file():
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
    
    # 安全检查，防止路径遍历攻击 (如 ../../etc/passwd)
    # filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if os.path.exists(file_path):
        try:
            # 1. 物理删除文件
            os.remove(file_path)
            
            # 2. TODO: 从向量数据库中删除对应的向量
            # collection.delete(where={"source": filename})
            # print(f"Vectors for {filename} deleted.")
            
            return jsonify({'message': f'File {filename} deleted successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)