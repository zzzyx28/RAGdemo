<template>
  <div>
  <v-navigation-drawer v-model="drawer" width="300" color="#f8f9fa" class="border-e">
    <div class="pa-4">
      <v-btn block color="primary" prepend-icon="mdi-plus" class="mb-4 text-none" elevation="0">
        新建知识库
      </v-btn>

      <div class="text-subtitle-2 text-grey-darken-1 mb-2 font-weight-bold">
        当前知识库 ({{ kbStats.fileCount }})
      </div>

      <v-list density="compact" nav bg-color="transparent" v-if="kbFiles.length > 0">
        <v-list-item
          v-for="(file, i) in kbFiles"
          :key="i"
          rounded="lg"
          :value="file.name"
          class="mb-1 knowledge-item"
        >
          <template v-slot:prepend>
            <v-icon :icon="getFileIcon(file.type)" :color="getFileColor(file.type)"></v-icon>
          </template>

          <v-list-item-title class="font-weight-medium text-body-2 text-truncate">{{ file.name }}</v-list-item-title>
          <v-list-item-subtitle class="text-caption" style="font-size: 10px !important;">{{
              file.size
            }}
          </v-list-item-subtitle>

          <template v-slot:append>
            <div class="d-flex align-center">
              <v-icon icon="mdi-check-circle" size="small" color="success" class="status-icon"></v-icon>

              <v-btn
                icon="mdi-trash-can-outline"
                size="x-small"
                variant="text"
                color="error"
                class="delete-btn ml-1"
                @click.stop="confirmDelete(file.name)"
              ></v-btn>
            </div>
          </template>
        </v-list-item>
      </v-list>

      <div v-else class="text-center py-10 text-grey-lighten-1">
        <v-icon icon="mdi-folder-open-outline" size="large" class="mb-2"></v-icon>
        <div class="text-caption">暂无文档，请上传</div>
      </div>

      <v-divider class="my-3"></v-divider>

      <div
        class="upload-zone pa-4 border-dashed rounded-lg text-center cursor-pointer position-relative"
        :class="{ 'bg-blue-lighten-5': isDragging }"
        @click="triggerUpload"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        style="transition: background-color 0.2s;"
      >
        <div v-if="isUploading" class="d-flex flex-column align-center justify-center py-2">
          <v-progress-circular indeterminate color="primary" size="24" class="mb-2"></v-progress-circular>
          <div class="text-caption text-primary">正在上传并索引...</div>
        </div>

        <div v-else class="text-grey-darken-1">
          <v-icon icon="mdi-cloud-upload" size="large" class="mb-2" :color="isDragging ? 'primary' : ''"></v-icon>
          <div class="text-caption">
            {{ isDragging ? '松开鼠标上传' : '点击或拖拽上传文档' }}
            <br><span class="text-grey-lighten-1" style="font-size: 10px">(支持 PDF, Word, MD)</span>
          </div>
        </div>

        <input
          type="file"
          ref="fileInput"
          style="display: none"
          @change="handleFileSelect"
          accept=".pdf,.md,.txt,.doc,.docx"
          multiple
        >
      </div>
    </div>
  </v-navigation-drawer>

  <v-app-bar flat color="transparent" class="px-4 mt-2 border-b-0">
    <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
    <v-btn variant="text" class="text-h6 font-weight-bold text-none">
      企业知识图谱
      <v-chip size="x-small" color="blue" class="ml-2" variant="flat">RAG开启</v-chip>
    </v-btn>
    <div class="mr-2">
      <v-menu v-if="isAuthenticated">
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            prepend-icon="mdi-account-circle"
            variant="flat"
            color="primary"
            class="text-none"
          >
            {{ currentUsername }}
          </v-btn>
        </template>

        <v-list density="compact">
          <v-list-item @click="handleLogout" prepend-icon="mdi-logout">
            <v-list-item-title>退出登录</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>

      <v-btn v-else color="primary" @click="handleLoginClick" prepend-icon="mdi-account-arrow-right">
        登录 / 注册
      </v-btn>
    </div>
  </v-app-bar>

  <v-main class="app-background">
    <v-container class="fill-height d-flex flex-column align-center" style="max-width: 900px;">

      <div v-if="messages.length === 0" class="text-center mt-15 fade-in">
        <h1 class="text-h4 font-weight-medium mb-2" style="color: #333;">你好，我是你的xxx知识助手</h1>
        <p class="text-grey">
          已接入 <b>{{ kbStats.fileCount }}</b> 个知识库文件
        </p>
      </div>

      <div v-else class="chat-history w-100 mb-4 overflow-y-auto px-2" style="flex: 1;" ref="chatContainer">
        <div v-for="(msg, index) in messages" :key="index" class="mb-6">
          <div v-if="msg.role === 'user'" class="d-flex justify-end">
            <v-sheet color="primary" class="pa-3 rounded-lg text-body-1" style="max-width: 80%;">
              {{ msg.content }}
            </v-sheet>
          </div>

          <div v-else class="d-flex align-start">
            <v-avatar color="teal-lighten-5" class="mr-3 mt-1" size="36">
              <v-icon icon="mdi-robot" color="teal"></v-icon>
            </v-avatar>
            <div style="max-width: 100%;">
              <div v-if="msg.isRagSearching" class="d-flex align-center text-caption text-blue mb-2">
                <v-progress-circular indeterminate size="16" width="2" color="blue"
                                     class="mr-2"></v-progress-circular>
                正在检索知识库...
              </div>

              <v-sheet class="pa-0 bg-transparent text-body-1 text-grey-darken-3">
                <div style="white-space: pre-wrap;">{{ msg.content }}</div>
              </v-sheet>
            </div>
          </div>
        </div>
      </div>

      <div class="w-100 pb-4 pt-2 bg-transparent" style="position: sticky; bottom: 0; z-index: 10;">
        <v-card class="input-card w-100 pa-2 rounded-xl elevation-3">
          <v-textarea
            v-model="inputMessage"
            variant="plain"
            placeholder="请输入您的问题..."
            auto-grow rows="1" max-rows="8" hide-details class="px-2"
            @keydown.enter.prevent="sendMessage"
          ></v-textarea>
          <div class="d-flex align-center px-2 pb-1 mt-2">
            <v-switch v-model="ragEnabled" density="compact" color="primary" hide-details label="RAG"
                      class="mr-4"></v-switch>
            <v-spacer></v-spacer>
            <v-btn icon="mdi-arrow-up" color="primary" class="rounded-circle" :disabled="!inputMessage || isLoading"
                   @click="sendMessage"></v-btn>
          </div>
        </v-card>
      </div>

    </v-container>
  </v-main>
  </div>
</template>

<script setup lang="ts">
import {ref, nextTick, onMounted, watch} from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// 添加认证状态管理
const isAuthenticated = ref(!!localStorage.getItem('access_token'))
const currentUsername = ref(localStorage.getItem('username') || '')

// 监听 storage 变化以响应登录/登出状态变化
const updateAuthState = () => {
  isAuthenticated.value = !!localStorage.getItem('access_token')
  currentUsername.value = localStorage.getItem('username') || ''
}
// 页面加载时更新认证状态
updateAuthState()

// 监听 localStorage 变化
window.addEventListener('storage', updateAuthState)

// 添加登出处理函数
const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('username')
  updateAuthState()
  router.push('/login')
}

// 【关键修改】处理登录点击：先清除旧Token，防止路由守卫循环跳转
const handleLoginClick = () => {
  console.log('点击了登录注册，清理旧状态...');
  localStorage.removeItem('access_token');
  localStorage.removeItem('username');
  isAuthenticated.value = false;
  router.push('/login');
}

// --- 定义状态 ---
const drawer = ref(true); // 默认打开侧边栏
const kbFiles = ref<any[]>([]); // 存储文件列表
const kbStats = ref({fileCount: 0, vectorCount: 0}); // 存储统计信息
const fileInput = ref<HTMLInputElement | null>(null);
const isUploading = ref(false); // 上传中状态
const isDragging = ref(false);  // 拖拽悬停状态
const ragEnabled = ref(true); // 默认开启RAG
interface Source {
  filename: string;
  page: number;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  isRagSearching?: boolean; // RAG 状态：是否正在检索
  sources?: Source[];    // RAG 结果：引用来源
}

const inputMessage = ref('');
const messages = ref<Message[]>([]);
const isLoading = ref(false);

// 触发点击
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
  isDragging.value = false;
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    uploadFiles(files);
  }
};

// 上传知识库\文件
const uploadFiles = async (fileList: FileList) => {
  isUploading.value = true;
  const formData = new FormData();

  // 将所有文件添加到 FormData
  Array.from(fileList).forEach((file) => {
    formData.append('file', file);
  });

  try {
    const response = await fetch('http://localhost:5000/api/upload', {
      method: 'POST',
      body: formData, // fetch 会自动设置 Content-Type 为 multipart/form-data
    });

    if (!response.ok) {
      const errData = await response.json();
      alert(`上传失败: ${errData.details || '未知错误'}`);
      return;
    }

    const data = await response.json();
    console.log('上传成功:', data);

    // 上传成功后，立即刷新知识库列表，更新界面
    await fetchKbInfo();

  } catch (error) {
    console.error('Network Error:', error);
    alert('网络错误，无法连接服务器');
  } finally {
    isUploading.value = false;
    // 清空 input，防止同名文件无法再次触发 change 事件
    if (fileInput.value) fileInput.value.value = '';
  }
};


// --- 删除文件逻辑 ---
const confirmDelete = async (filename: string) => {
  if (!confirm(`确定删除 "${filename}" 吗？`)) return;

  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('请先登录');
      return;
    }

    // 严格按照后端要求传递filename参数
    const response = await fetch('http://localhost:5000/api/delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` // 补充认证头
      },
      body: JSON.stringify({ filename: filename }), // 与后端参数名完全匹配
    });

    if (response.ok) {
      await fetchKbInfo(); // 刷新文件列表
    } else {
      const err = await response.json();
      alert(`删除失败: ${err.error || '未知错误'}`);
    }
  } catch (error) {
    console.error('删除错误:', error);
    alert('网络错误，无法连接服务器');
  }
};


// --- 获取知识库信息 ---
const fetchKbInfo = async () => {
  // try {
  //   const res = await fetch('http://localhost:5000/api/kb-info');
  //   const data = await res.json();
  //   kbFiles.value = data.files;
  //   kbStats.value = {
  //     fileCount: data.file_count,
  //     vectorCount: data.vector_count
  //   };
  // } catch (error) {
  //   console.error("获取知识库信息失败:", error);
  // }
};

// 组件加载时获取数据
onMounted(() => {
  updateAuthState();
  fetchKbInfo();
});

// --- UI 辅助函数 ---
const formatNumber = (num: number) => {
  return new Intl.NumberFormat('en-US').format(num);
};

const getFileIcon = (type: string) => {
  switch (type) {
    case 'pdf':
      return 'mdi-file-pdf-box';
    case 'md':
      return 'mdi-language-markdown';
    case 'doc':
    case 'docx':
      return 'mdi-file-word-box';
    case 'txt':
      return 'mdi-file-document-outline';
    default:
      return 'mdi-file';
  }
};

const getFileColor = (type: string) => {
  switch (type) {
    case 'pdf':
      return 'red-darken-1';
    case 'md':
      return 'black';
    case 'docx':
      return 'blue-darken-2';
    default:
      return 'grey';
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return;

  const userText = inputMessage.value;
  messages.value.push({role: 'user', content: userText});
  inputMessage.value = '';
  isLoading.value = true;

  // 核心修改：获取 Token 并添加到 Headers
  const token = localStorage.getItem('access_token');
  if (!token) {
    alert("请先登录！");
    isLoading.value = false;
    return;
  }

  try {
    // 1. 先创建一个空的助手消息，状态为"正在检索"
    const assistantMsgIndex = messages.value.push({
      role: 'assistant',
      content: '',
      isRagSearching: ragEnabled.value,
      sources: []
    }) - 1;

    const response = await fetch('http://localhost:5000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message: userText,
        use_rag: ragEnabled.value
      }),
    });

    // 处理认证错误
    if (response.status === 401) {
      alert('登录状态已失效，请重新登录。');
      localStorage.removeItem('access_token');
      localStorage.removeItem('username');
      router.push('/login');
      isLoading.value = false;
      // 移除刚添加的助手消息
      if (messages.value.length > 0) {
        const lastMsg = messages.value[messages.value.length - 1];
        if (lastMsg?.role === 'assistant') {
          messages.value.pop();
        }
      }
      return;
    }

    // 处理 422 错误（JWT token 无效）
    if (response.status === 422) {
      const errorData = await response.json();
      alert(`认证失败: ${errorData.msg || errorData.message || 'Token 无效，请重新登录'}`);
      localStorage.removeItem('access_token');
      localStorage.removeItem('username');
      router.push('/login');
      isLoading.value = false;
      // 移除刚添加的助手消息
      if (messages.value.length > 0) {
        const lastMsg2 = messages.value[messages.value.length - 1];
        if (lastMsg2?.role === 'assistant') {
          messages.value.pop();
        }
      }
      return;
    }

    // 处理其他错误状态码
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: '未知错误' }));
      const lastIndex = messages.value.length - 1;
      if (lastIndex >= 0) {
        const assistantMsg = messages.value[lastIndex];
        if (assistantMsg && assistantMsg.role === 'assistant') {
          assistantMsg.content = `请求失败: ${errorData.error || errorData.message || '服务器错误'}`;
          assistantMsg.isRagSearching = false;
        }
      }
      isLoading.value = false;
      return;
    }

    // 检查响应体是否存在
    if (!response.body) {
      const lastIndex = messages.value.length - 1;
      if (lastIndex >= 0) {
        const assistantMsg = messages.value[lastIndex];
        if (assistantMsg && assistantMsg.role === 'assistant') {
          assistantMsg.content = "服务器未返回数据";
          assistantMsg.isRagSearching = false;
        }
      }
      isLoading.value = false;
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, {stream: true});
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6);
          if (dataStr === '[DONE]') break;

          const data = JSON.parse(dataStr);

          // 2. 处理特定事件：检索完成
          const assistantMsg = messages.value[assistantMsgIndex];
          if (!assistantMsg) continue;

          if (data.type === 'searching_end') {
            assistantMsg.isRagSearching = false;
            if (data.sources) {
              assistantMsg.sources = data.sources;
            }
          }
          // 3. 处理流式文本
          else if (data.content) {
            assistantMsg.isRagSearching = false;
            assistantMsg.content += data.content;
          }
        }
      }
    }
  } catch (e) {
    console.error(e);
    const lastIndex = messages.value.length - 1;
    if (lastIndex >= 0) {
      const assistantMsg = messages.value[lastIndex];
      if (assistantMsg && assistantMsg.role === 'assistant') {
        assistantMsg.content = "系统错误，请检查后端连接。";
        assistantMsg.isRagSearching = false;
      }
    }
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.app-background {
  background-color: #fbfbfb;
}

.border-dashed {
  border: 2px dashed #e0e0e0;
}

.input-card {
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.input-card:focus-within {
  border-color: #2196F3;
  box-shadow: 0 4px 20px rgba(33, 150, 243, 0.15) !important;
}

/* 让删除按钮默认隐藏，悬停时显示 */
.delete-btn {
  display: none;
}

.knowledge-item:hover .delete-btn {
  display: inline-flex;
}

.knowledge-item:hover .status-icon {
  display: none; /* 悬停时隐藏绿勾，显示垃圾桶 */
}
</style>
