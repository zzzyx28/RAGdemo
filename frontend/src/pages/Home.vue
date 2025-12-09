<template>
  <div>
    <KnowledgeBaseSidebar
      v-model="drawer"
      :kb-files="kbFiles"
      :kb-stats="kbStats"
      :is-uploading="isUploading"
      :get-file-icon="getFileIcon"
      :get-file-color="getFileColor"
      :handle-file-select="handleFileSelect"
      :handle-drop="handleDrop"
      @delete-file="confirmDelete"
    />

    <v-app-bar fixed flat color="white" class="px-4 border-b-0 elevation-1">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-btn variant="text" class="text-h6 font-weight-bold text-none">
        企业知识图谱
        <v-chip size="x-small" color="blue" class="ml-2" variant="flat">RAG开启</v-chip>
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
      <v-container class="chat-container d-flex flex-column" style="max-width: 900px; height: 100%; padding-top: 16px; padding-bottom: 16px;">

        <div v-if="messages.length === 0" class="text-center fade-in welcome-section">
          <h1 class="text-h4 font-weight-medium mb-2" style="color: #333;">你好，我是你的 xxx 知识助手</h1>
          <p class="text-grey">
            已接入 <b>{{ kbStats.fileCount }}</b> 个知识库文件
          </p>
        </div>

        <div v-else class="chat-history w-100 overflow-y-auto px-2" ref="chatContainer">
          <div v-for="(msg, index) in messages" :key="index" class="message-item mb-6">

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
                <v-icon icon="mdi-robot" color="teal-darken-1"></v-icon>
              </v-avatar>
              <div class="assistant-message" style="max-width: calc(100% - 48px);">

                <div v-if="msg.isRagSearching" class="d-flex align-center text-caption text-blue mb-2">
                  <v-progress-circular indeterminate size="16" width="2" color="blue"
                                       class="mr-2"></v-progress-circular>
                  正在检索知识库...
                </div>

                <v-sheet
                  class="pa-3 text-body-1 message-bubble assistant-message-bubble"
                  style="background-color: #f5f5f5; word-wrap: break-word;"
                  :class="{'mt-2': msg.isRagSearching && !msg.content}"
                >
                  <div style="white-space: pre-wrap; color: #333;">{{ msg.content || '正在思考...' }}</div>
                </v-sheet>

                <div
                  v-if="msg.sources && msg.sources.length && msg.content"
                  class="mt-2 text-caption text-grey-darken-1 d-flex flex-wrap align-start"
                >
                  <v-icon size="small" icon="mdi-lightbulb-on-outline" class="mr-1 mt-1"></v-icon>
                  <div class="font-weight-medium mr-2 mt-1">参考来源:</div>
                  <v-chip
                    v-for="(source, sIndex) in msg.sources"
                    :key="sIndex"
                    size="x-small"
                    class="ml-0 mr-1 mt-1"
                    color="grey-lighten-3"
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
          <v-card class="input-card w-100 pa-2 rounded-xl elevation-3">
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
import KnowledgeBaseSidebar from '@/components/KnowledgeBaseSidebar.vue';
import { useAuth } from '@/composables/useAuth';
import { useSnackbar } from '@/composables/useSnackbar';
import { useKnowledgeBase } from '@/composables/useKnowledgeBase';
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

const {
  messages,
  inputMessage,
  isLoading,
  ragEnabled,
  chatContainer,
  sendMessage,
  handleKeyDown
} = useChat(isAuthenticated, showSnackbar);

// 侧边栏状态
const drawer = ref(true);

// 监听登录状态变化，登录后自动刷新知识库信息
watch(isAuthenticated, (newVal, oldVal) => {
  // 当从未登录变为已登录时，刷新知识库信息
  if (newVal && !oldVal) {
    fetchKbInfo();
  } else if (!newVal && oldVal) {
    // 登出时清空知识库信息
    kbFiles.value = [];
    kbStats.value = { fileCount: 0, vectorCount: 0 };
  }
});

// 组件加载时获取数据
onMounted(() => {
  // 确保认证状态是最新的
  updateAuthState();
  // 获取知识库信息（如果已登录）
  fetchKbInfo();
});
</script>

<style scoped>
.app-background {
  background-color: #fbfbfb;
  padding-top: 64px !important;
  height: 100vh;
  overflow: hidden;
}

.chat-container {
  position: relative;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-history {
  flex: 1;
  min-height: 0;
  padding-top: 16px;
  padding-bottom: 16px;
  scroll-behavior: smooth;
  /* 自定义滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

.chat-history::-webkit-scrollbar {
  width: 6px;
}

.chat-history::-webkit-scrollbar-track {
  background: transparent;
}

.chat-history::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.chat-history::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
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
  background-color: #fbfbfb;
  position: relative;
  z-index: 10;
}

.input-card {
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.input-card:focus-within {
  border-color: #2196F3;
  box-shadow: 0 4px 20px rgba(33, 150, 243, 0.15) !important;
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
  /* 现代非对称圆角 */
  border-radius: 18px 18px 6px 18px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.assistant-message-bubble {
  /* 现代非对称圆角 */
  border-radius: 18px 18px 18px 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0e0e0;
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
