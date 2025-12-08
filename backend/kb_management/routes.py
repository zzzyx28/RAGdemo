import os
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename

# 从 extensions 中导入 db, 虽然这里主要处理文件系统，但保持一致性
# 如果未来删除操作需要连接 db (删除向量)，则需要 db
from ..extensions import db

from .__init__ import kb_bp  # 导入蓝图实例

# 配置 (与 app.py 中保持一致或从 config.py 导入)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'doc', 'docx', 'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ----------------------------------------------------------------
# 获取知识库信息接口 (真实读取文件夹和向量库状态)
# ----------------------------------------------------------------
@kb_bp.route('/kb-info', methods=['GET'])
def get_kb_info():
    upload_folder = current_app.config.get('UPLOAD_FOLDER', UPLOAD_FOLDER)
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


@kb_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    files = request.files.getlist('file')  # 支持多文件上传
    saved_files = []
    errors = []

    upload_folder = current_app.config.get('UPLOAD_FOLDER', UPLOAD_FOLDER)
    for file in files:
        if file.filename == '':
            continue

        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            filename = file.filename
            file_path = os.path.join(upload_folder, filename)

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
@kb_bp.route('/delete', methods=['POST'])
def delete_file():
    data = request.json
    filename = data.get('filename')

    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    upload_folder = current_app.config.get('UPLOAD_FOLDER', UPLOAD_FOLDER)

    # 安全检查，防止路径遍历攻击 (如 ../../etc/passwd)
    # filename = secure_filename(filename)
    file_path = os.path.join(upload_folder, filename)

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