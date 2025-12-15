<template>
  <div>
    <UnifiedSidebar
      v-model="drawer"
      :conversations="conversations"
      :selected-conversation-id="currentConversationId"
      :kb-files="kbFiles"
      :kb-stats="kbStats"
      :is-uploading="isUploading"
      :get-file-icon="getFileIcon"
      :get-file-color="getFileColor"
      :handle-file-select="handleFileSelect"
      :handle-drop="handleDrop"
      @select="handleSelectConversation"
      @new="handleNewConversation"
      @delete="handleDeleteConversation"
      @rename="handleRenameConversation"
      @delete-file="confirmDelete"
    />

    <v-app-bar fixed flat color="white" class="px-4" style="box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-bottom: none;">
      <v-app-bar-nav-icon @click="drawer = !drawer" color="primary"></v-app-bar-nav-icon>
      <v-btn variant="text" class="text-h6 font-weight-bold text-none">
        企业知识图谱
        <v-chip size="x-small" color="blue" class="ml-2" variant="flat">RAG</v-chip>
      </v-btn>
      <v-spacer></v-spacer>
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

        <v-btn
          v-else
          color="primary"
          @click="handleLoginClick"
          append-icon="mdi-account-arrow-right"
          class="text-none"
        >
          登录 / 注册
        </v-btn>
      </div>
    </v-app-bar>

    <v-main class="app-background">
      <v-container class="chat-container d-flex flex-column" style="max-width: 900px; height: 100%; padding-top: 24px; padding-bottom: 24px;">

        <div v-if="messages.length === 0" class="text-center fade-in welcome-section">
          <h1 class="text-h4 font-weight-bold mb-3" style="color: #2c3e50; letter-spacing: 0.5px; font-weight: 500;">你好，我是你的知识助手</h1>
          <p class="text-body-1" style="color: #7f8c8d;">
            已接入 {{ kbStats.fileCount }} 个知识库文件
          </p>
        </div>

        <div v-else class="chat-history w-100 overflow-y-auto px-2" ref="chatContainer">
          <div v-for="(msg, index) in messages" :key="msg.id || index" class="message-item mb-8">

            <div v-if="msg.role === 'user'" class="d-flex justify-end">
              <v-sheet
                color="primary"
                class="pa-3 text-body-1 message-bubble user-message"
                style="max-width: 80%; word-wrap: break-word;"
              >
                <div style="white-space: pre-wrap; color: white;">{{ msg.content }}</div>
              </v-sheet>
            </div>

            <div v-else class="d-flex align-start">
              <v-avatar color="teal-lighten-5" class="mr-3 mt-1" size="36">
                <v-icon icon="mdi-robot" color="blue-darken-1"></v-icon>
              </v-avatar>
              <div class="assistant-message" style="max-width: calc(100% - 48px);">

                <div v-if="msg.isRagSearching" class="d-flex align-center text-caption mb-2" style="color: #2196F3;">
                  <v-progress-circular indeterminate size="16" width="2" color="blue"
                                       class="mr-2"></v-progress-circular>
                  正在检索知识库...
                </div>

                <v-sheet
                  class="pa-3 text-body-1 message-bubble assistant-message-bubble"
                  style="background-color: #ffffff; word-wrap: break-word;"
                  :class="{'mt-2': msg.isRagSearching && !msg.content}"
                >
                  <div style="white-space: pre-wrap; color: #2c3e50;">{{ msg.content || '正在思考...' }}</div>
                </v-sheet>

                <div
                  v-if="msg.sources && msg.sources.length && msg.content"
                  class="mt-2 text-caption d-flex flex-wrap align-start"
                  style="color: #7f8c8d;"
                >
                  <v-icon size="small" icon="mdi-lightbulb-on-outline" class="mr-1 mt-1"></v-icon>
                  <div class="font-weight-medium mr-2 mt-1">参考来源:</div>
                  <v-chip
                    v-for="(source, sIndex) in msg.sources"
                    :key="sIndex"
                    size="x-small"
                    class="ml-0 mr-1 mt-1"
                    style="background-color: #f0f0f0; color: #5a6c7d;"
                    variant="flat"
                  >
                    {{ source.filename }} (P{{ source.page }})
                  </v-chip>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="w-100 input-wrapper">
          <v-card class="input-card w-100 pa-2 rounded-xl" style="box-shadow: 0 2px 12px rgba(0,0,0,0.08);">
            <v-textarea
              v-model="inputMessage"
              variant="plain"
              placeholder="请输入您的问题..."
              auto-grow rows="1" max-rows="8" hide-details class="px-2"
              @keydown="handleKeyDown"
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

    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      multi-line
    >
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn
          :color="snackbar.color === 'error' ? 'white' : 'white'"
          variant="text"
          @click="snackbar.show = false"
        >
          关闭
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import UnifiedSidebar from '@/components/UnifiedSidebar.vue';
import { useAuth } from '@/composables/useAuth';
import { useSnackbar } from '@/composables/useSnackbar';
import { useKnowledgeBase } from '@/composables/useKnowledgeBase';
import { useConversationHistory } from '@/composables/useConversationHistory';
import { useChat } from '@/composables/useChat';

// 使用 composables
const { isAuthenticated, currentUsername, handleLogout, handleLoginClick, updateAuthState } = useAuth();
const { snackbar, showSnackbar, parseErrorMsg } = useSnackbar();
const {
  kbFiles,
  kbStats,
  isUploading,
  fetchKbInfo,
  confirmDelete,
  handleFileSelect,
  handleDrop,
  getFileIcon,
  getFileColor
} = useKnowledgeBase(isAuthenticated, showSnackbar, parseErrorMsg);

// 对话历史管理
const {
  conversations,
  currentConversationId,
  fetchConversations,
  createConversation,
  fetchConversation,
  updateConversationTitle,
  deleteConversation,
  selectConversation,
  clearCurrentConversation
} = useConversationHistory(isAuthenticated, showSnackbar);

// 确保 currentConversationId 被正确传递
console.log('[Home] 初始化 useChat, currentConversationId:', currentConversationId.value);

const {
  messages,
  inputMessage,
  isLoading,
  ragEnabled,
  chatContainer,
  sendMessage,
  handleKeyDown,
  loadMessages,
  clearMessages
} = useChat(isAuthenticated, showSnackbar, currentConversationId, fetchConversations);

// 监听 currentConversationId 的变化，用于调试
watch(currentConversationId, (newId, oldId) => {
  console.log('[Home] currentConversationId 变化:', { oldId, newId });
}, { immediate: true });

// 侧边栏状态
const drawer = ref(true);

// 监听登录状态变化，登录后自动刷新知识库信息和对话历史
watch(isAuthenticated, (newVal, oldVal) => {
  // 当从未登录变为已登录时，刷新知识库信息和对话历史
  if (newVal && !oldVal) {
    fetchKbInfo();
    fetchConversations();
  } else if (!newVal && oldVal) {
    // 登出时清空知识库信息和对话历史
    kbFiles.value = [];
    kbStats.value = { fileCount: 0, vectorCount: 0 };
    conversations.value = [];
    clearCurrentConversation();
    clearMessages();
  }
});

// 处理对话选择
const handleSelectConversation = async (conversationId: number | null) => {
  if (!conversationId) {
    clearCurrentConversation();
    clearMessages();
    return;
  }

  // 如果选择的是当前对话，不需要重新加载
  if (currentConversationId.value === conversationId) {
    return;
  }

  selectConversation(conversationId);
  const conversation = await fetchConversation(conversationId);
  if (conversation && conversation.messages) {
    loadMessages(conversation.messages);
  } else {
    // 如果没有消息，清空消息列表
    clearMessages();
  }
};

// 处理新建对话
const handleNewConversation = () => {
  // 清空当前对话ID和消息，下次发送消息时会自动创建新对话
  clearCurrentConversation();
  clearMessages();
  // 确保界面滚动到顶部
  if (chatContainer.value) {
    chatContainer.value.scrollTop = 0;
  }
};

// 处理删除对话
const handleDeleteConversation = async (conversationId: number) => {
  if (currentConversationId.value === conversationId) {
    clearCurrentConversation();
    clearMessages();
  }
  await deleteConversation(conversationId);
};

// 处理重命名对话
const handleRenameConversation = async (conversationId: number, newTitle: string) => {
  await updateConversationTitle(conversationId, newTitle);
};

// 监听当前对话ID变化（用于调试和选择对话时）
watch(currentConversationId, (newId, oldId) => {
  console.log('[Home] currentConversationId watch 触发:', { oldId, newId });
  // 只在从无到有或切换对话时刷新，避免重复刷新
  if (newId && newId !== oldId) {
    // 选择对话时不需要刷新，因为已经在 handleSelectConversation 中处理了
  }
}, { immediate: true });

// 组件加载时获取数据
onMounted(() => {
  // 确保认证状态是最新的
  updateAuthState();
  // 获取知识库信息和对话历史（如果已登录）
  if (isAuthenticated.value) {
    fetchKbInfo();
    fetchConversations();
  }
});
</script>

<style scoped>
.app-background {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding-top: 64px !important;
  min-height: 100vh;
  overflow: hidden;
  transition: margin-left 0.3s ease;
}

.chat-container {
  position: relative;
  overflow: hidden;
  min-height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  background: transparent;
  margin: 0 auto;
}

.chat-history {
  flex: 1;
  min-height: 0;
  padding-top: 20px;
  padding-bottom: 20px;
  scroll-behavior: smooth;
  /* 自定义滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.15) transparent;
}

.chat-history::-webkit-scrollbar {
  width: 6px;
}

.chat-history::-webkit-scrollbar-track {
  background: transparent;
}

.chat-history::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.25);
}

.welcome-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.input-wrapper {
  flex-shrink: 0;
  padding-top: 16px;
  background-color: transparent;
  position: relative;
  z-index: 10;
}

.input-card {
  border: none;
  background: white;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.input-card:focus-within {
  box-shadow: 0 4px 20px rgba(33, 150, 243, 0.15) !important;
  transform: translateY(-1px);
}

/* 消息气泡样式优化 */
.message-item {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-bubble {
  word-break: break-word;
  line-height: 1.6;
}

.user-message {
  border-radius: 20px 20px 6px 20px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.assistant-message-bubble {
  border-radius: 20px 20px 20px 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  border: none;
  background: white;
}

/* 响应式优化 */
@media (max-width: 600px) {
  .chat-container {
    padding-left: 8px;
    padding-right: 8px;
  }

  .chat-history {
    padding-left: 4px;
    padding-right: 4px;
  }

  .message-item {
    margin-bottom: 12px !important;
  }

  .user-message,
  .assistant-message {
    max-width: 90% !important;
  }

  .input-card {
    margin: 0 4px;
  }
}
</style>
