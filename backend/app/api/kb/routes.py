"""
知识库管理路由
"""
import os
from flask import request, current_app
from werkzeug.utils import secure_filename

from app.utils.responses import APIResponse
from . import kb_bp

# 从配置中获取上传配置
def get_upload_config():
    """获取上传配置"""
    return {
        'folder': current_app.config.get('UPLOAD_FOLDER'),
        'max_size': current_app.config.get('MAX_UPLOAD_SIZE', 10485760),
        'allowed_extensions': current_app.config.get('ALLOWED_EXTENSIONS', {'txt', 'pdf', 'md', 'doc', 'docx', 'csv'})
    }


def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@kb_bp.route('/kb-info', methods=['GET'])
def get_kb_info():
    """获取知识库信息接口"""
    config = get_upload_config()
    upload_folder = config['folder']
    
    # 获取真实文件列表
    files = []
    if os.path.exists(upload_folder):
        for f in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, f)
            if os.path.isfile(file_path) and not f.startswith('.'):
                size_kb = os.path.getsize(file_path) / 1024
                files.append({
                    "name": f,
                    "size": f"{size_kb:.1f} KB",
                    "type": f.split('.')[-1].lower()
                })
    
    # 模拟向量数量（实际应从 ChromaDB 查询）
    vector_count = len(files) * 52
    
    return APIResponse.success(
        data={
            "file_count": len(files),
            "vector_count": vector_count,
            "files": files
        },
        message="获取成功"
    )


@kb_bp.route('/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    if 'file' not in request.files:
        return APIResponse.error(message="No file part", code=400)
    
    config = get_upload_config()
    files = request.files.getlist('file')  # 支持多文件上传
    saved_files = []
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
        
        # 检查文件扩展名
        if not allowed_file(file.filename, config['allowed_extensions']):
            errors.append(f"文件 {file.filename} 类型不允许")
            continue
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > config['max_size']:
            errors.append(f"文件 {file.filename} 超过大小限制")
            continue
        
        # 保存文件
        filename = secure_filename(file.filename)
        file_path = os.path.join(config['folder'], filename)
        
        try:
            file.save(file_path)
            saved_files.append(filename)
            current_app.logger.info(f"文件上传成功: {filename}")
            
            # TODO: 触发异步任务进行向量化
            # 1. 读取文件内容 (Loader)
            # 2. 文本切片 (Splitter)
            # 3. 向量化并存入 ChromaDB (Vector Store)
            
        except (OSError, IOError) as e:
            current_app.logger.error(f"保存文件失败 {filename}: {str(e)}")
            errors.append(f"保存文件 {file.filename} 失败: {str(e)}")
    
    if not saved_files and errors:
        return APIResponse.error(
            message="上传失败",
            errors={"details": errors},
            code=400
        )
    
    return APIResponse.success(
        data={
            "files": saved_files,
            "errors": errors
        },
        message=f"成功上传 {len(saved_files)} 个文件"
    )


@kb_bp.route('/delete', methods=['POST'])
def delete_file():
    """删除文件接口"""
    data = request.get_json()
    filename = data.get('filename') if data else None
    
    if not filename:
        return APIResponse.error(message="Filename is required", code=400)
    
    config = get_upload_config()
    
    # 安全检查，防止路径遍历攻击
    filename = secure_filename(filename)
    file_path = os.path.join(config['folder'], filename)
    
    # 确保文件在允许的目录内
    if not os.path.abspath(file_path).startswith(os.path.abspath(config['folder'])):
        return APIResponse.error(message="Invalid file path", code=400)
    
    if os.path.exists(file_path):
        try:
            # 1. 物理删除文件
            os.remove(file_path)
            
            # 2. TODO: 从向量数据库中删除对应的向量
            # collection.delete(where={"source": filename})
            
            current_app.logger.info(f"文件删除成功: {filename}")
            return APIResponse.success(message=f"文件 {filename} 删除成功")
        except (OSError, IOError) as e:
            current_app.logger.error(f"删除文件失败 {filename}: {str(e)}")
            return APIResponse.server_error(f"删除文件失败: {str(e)}")
    else:
        return APIResponse.not_found("文件不存在")

