import { ref, type Ref } from 'vue';
import type { KnowledgeFile } from '@/types/chat';

export function useKnowledgeBase(
  isAuthenticated: Ref<boolean>,
  showSnackbar: (text: string, color?: 'success' | 'error' | 'warning' | 'info') => void,
  parseErrorMsg: (result: any) => string
) {
  const kbFiles = ref<KnowledgeFile[]>([]);
  const kbStats = ref({ fileCount: 0, vectorCount: 0 });
  const fileInput = ref<HTMLInputElement | null>(null);
  const isUploading = ref(false);

  // 获取知识库信息
  const fetchKbInfo = async () => {
    // 如果未登录，不获取知识库信息，保持空状态
    if (!isAuthenticated.value) {
      kbFiles.value = [];
      kbStats.value = { fileCount: 0, vectorCount: 0 };
      return;
    }

    try {
      const { get } = await import('@/utils/api');
      const result = await get('/kb-info');

      if (result.code === 200) {
        kbFiles.value = result.data?.files || [];
        kbStats.value = {
          fileCount: result.data?.file_count || 0,
          vectorCount: result.data?.vector_count || 0
        };
      } else {
        // 如果是认证错误，不显示错误提示（因为可能是未登录状态）
        if (result.code !== 401 && result.code !== 422) {
          console.error("获取知识库信息失败:", result.message || '未知错误');
        }
        kbFiles.value = [];
        kbStats.value = { fileCount: 0, vectorCount: 0 };
      }
    } catch (error) {
      // 网络错误时静默处理，不显示错误提示
      console.error("获取知识库信息失败:", error);
      kbFiles.value = [];
      kbStats.value = { fileCount: 0, vectorCount: 0 };
    }
  };

  // 上传知识库文件
  const uploadFiles = async (fileList: FileList) => {
    // 检查登录状态
    if (!isAuthenticated.value) {
      showSnackbar('请先登录后再上传文件', 'warning');
      if (fileInput.value) fileInput.value.value = '';
      return;
    }

    isUploading.value = true;
    const formData = new FormData();
    Array.from(fileList).forEach((file) => {
      formData.append('file', file);
    });

    try {
      const { upload } = await import('@/utils/api');
      const result = await upload('/upload', formData);

      if (result.code !== 200) {
        const errorMsg = parseErrorMsg(result);
        showSnackbar(`上传失败: ${errorMsg}`, 'error');
        return;
      }

      showSnackbar(`成功上传 ${fileList.length} 个文件并开始索引`, 'success');
      await fetchKbInfo(); // 刷新知识库列表

    } catch (error: any) {
      console.error('Network Error:', error);
      showSnackbar(error.message || '网络错误，无法连接服务器', 'error');
    } finally {
      isUploading.value = false;
      if (fileInput.value) fileInput.value.value = '';
    }
  };

  // 删除文件逻辑
  const confirmDelete = async (filename: string) => {
    // 检查登录状态
    if (!isAuthenticated.value) {
      showSnackbar('请先登录后再删除文件', 'warning');
      return;
    }

    if (!confirm(`确定删除 "${filename}" 吗？此操作不可逆。`)) return;

    try {
      const { post } = await import('@/utils/api');
      const result = await post('/delete', { filename: filename });

      if (result.code === 200) {
        showSnackbar(`文件 "${filename}" 删除成功。`, 'success');
        await fetchKbInfo(); // 刷新文件列表
      } else {
        const errorMsg = parseErrorMsg(result);
        showSnackbar(`删除失败: ${errorMsg}`, 'error');
      }
    } catch (error: any) {
      console.error('删除错误:', error);
      showSnackbar(error.message || '网络错误，无法连接服务器', 'error');
    }
  };

  // 触发点击上传
  const triggerUpload = () => {
    if (!isUploading.value) fileInput.value?.click();
  };

  // 处理点击选择文件
  const handleFileSelect = (e: Event) => {
    const files = (e.target as HTMLInputElement).files;
    if (files && files.length > 0) {
      uploadFiles(files);
    }
  };

  // 处理拖拽放下文件
  const handleDrop = (e: DragEvent) => {
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      uploadFiles(files);
    }
  };

  // UI 辅助函数
  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf': return 'mdi-file-pdf-box';
      case 'md':
      case 'txt': return 'mdi-language-markdown';
      case 'doc':
      case 'docx': return 'mdi-file-word-box';
      default: return 'mdi-file';
    }
  };

  const getFileColor = (type: string) => {
    switch (type) {
      case 'pdf': return 'red-darken-1';
      case 'md': return 'black';
      case 'docx':
      case 'doc': return 'blue-darken-2';
      default: return 'grey';
    }
  };

  return {
    kbFiles,
    kbStats,
    fileInput,
    isUploading,
    fetchKbInfo,
    uploadFiles,
    confirmDelete,
    triggerUpload,
    handleFileSelect,
    handleDrop,
    getFileIcon,
    getFileColor
  };
}

