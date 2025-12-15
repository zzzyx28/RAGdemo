<template>
  <v-navigation-drawer
    v-model="localDrawer"
    permanent
    location="left"
    width="320"
    class="unified-sidebar"
    elevation="0"
  >
    <!-- 顶部按钮栏 -->
    <v-tabs
      v-model="activeTab"
      bg-color="primary"
      color="white"
      density="compact"
      class="sidebar-tabs"
      slider-color="white"
      style="box-shadow: 0 1px 3px rgba(0,0,0,0.05);"
    >
      <v-tab value="history" class="text-none" style="min-width: 50%;">
        <v-icon icon="mdi-message-text" class="mr-2" size="small"></v-icon>
        历史对话
      </v-tab>
      <v-tab value="knowledge" class="text-none" style="min-width: 50%;">
        <v-icon icon="mdi-book-open-variant" class="mr-2" size="small"></v-icon>
        知识库
      </v-tab>
    </v-tabs>

    <!-- 内容区域 -->
    <v-window v-model="activeTab" class="sidebar-content">
      <!-- 历史对话内容 -->
      <v-window-item value="history">
        <div class="pa-3">
          <div class="d-flex align-center justify-space-between pa-2 mb-3">
            <v-toolbar-title class="text-subtitle-1 font-weight-bold text-grey-darken-2">对话历史</v-toolbar-title>
            <v-btn
              icon="mdi-plus"
              size="small"
              variant="flat"
              color="primary"
              @click="handleNewConversation"
              title="新建对话"
              class="elevation-1"
            ></v-btn>
          </div>

          <v-list density="compact" nav class="px-1">
            <v-list-item
              v-for="conv in conversations"
              :key="conv.id"
              :active="selectedConversationId === conv.id"
              @click="handleSelectConversation(conv.id)"
              class="conversation-item mb-1"
              rounded="lg"
              :class="{ 'conversation-active': selectedConversationId === conv.id }"
            >
              <template v-slot:prepend>
                <v-icon icon="mdi-message-text" class="mr-2" size="small"></v-icon>
              </template>

              <v-list-item-title class="text-body-2 conversation-title">
                {{ conv.title }}
              </v-list-item-title>

              <v-list-item-subtitle class="text-caption text-grey">
                {{ formatDate(conv.updated_at) }}
              </v-list-item-subtitle>

              <template v-slot:append>
                <v-menu location="bottom">
                  <template v-slot:activator="{ props }">
                    <v-btn
                      icon="mdi-dots-vertical"
                      size="x-small"
                      variant="text"
                      v-bind="props"
                      @click.stop
                    ></v-btn>
                  </template>
                  <v-list density="compact">
                    <v-list-item @click.stop="handleRenameConversation(conv)">
                      <v-list-item-title>重命名</v-list-item-title>
                      <template v-slot:prepend>
                        <v-icon icon="mdi-pencil" size="small"></v-icon>
                      </template>
                    </v-list-item>
                    <v-list-item @click.stop="handleDeleteConversation(conv.id)">
                      <v-list-item-title>删除</v-list-item-title>
                      <template v-slot:prepend>
                        <v-icon icon="mdi-delete" size="small" color="error"></v-icon>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </template>
            </v-list-item>

            <v-list-item v-if="conversations.length === 0" class="text-center text-grey py-8">
              <div class="d-flex flex-column align-center w-100">
                <v-icon icon="mdi-message-text-outline" size="48" color="grey-lighten-1" class="mb-2"></v-icon>
                <v-list-item-title class="text-caption">
                  暂无对话记录
                </v-list-item-title>
              </div>
            </v-list-item>
          </v-list>
        </div>
      </v-window-item>

      <!-- 知识库内容 -->
      <v-window-item value="knowledge">
        <div class="pa-3">
          <v-btn 
            block 
            color="primary" 
            prepend-icon="mdi-plus" 
            class="mb-4 text-none elevation-2" 
            disabled
            variant="flat"
          >
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
                    @click.stop="$emit('delete-file', file.name)"
                    title="删除知识库文件"
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
            class="upload-zone pa-4 rounded-lg text-center cursor-pointer position-relative"
            :class="{ 'bg-blue-lighten-5': isDragging }"
            @click="triggerUpload"
            @dragover.prevent="handleDragover"
            @dragleave.prevent="handleDragleave"
            @drop.prevent="handleDropInternal"
            style="transition: background-color 0.2s; border: 2px dashed rgba(0,0,0,0.1);"
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
      </v-window-item>
    </v-window>

    <!-- 重命名对话框 -->
    <v-dialog v-model="renameDialog" max-width="400">
      <v-card>
        <v-card-title>重命名对话</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="renameTitle"
            label="对话标题"
            variant="outlined"
            autofocus
            @keydown.enter="confirmRename"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="renameDialog = false">取消</v-btn>
          <v-btn color="primary" variant="flat" @click="confirmRename">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Conversation, KnowledgeFile } from '@/types/chat';

interface Props {
  modelValue: boolean;
  // 历史对话相关
  conversations: Conversation[];
  selectedConversationId: number | null;
  // 知识库相关
  kbFiles: KnowledgeFile[];
  kbStats: { fileCount: number; vectorCount: number };
  isUploading: boolean;
  getFileIcon: (type: string) => string;
  getFileColor: (type: string) => string;
  handleFileSelect: (e: Event) => void;
  handleDrop: (e: DragEvent) => void;
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void;
  // 历史对话事件
  (e: 'select', conversationId: number | null): void;
  (e: 'new'): void;
  (e: 'delete', conversationId: number): void;
  (e: 'rename', conversationId: number, newTitle: string): void;
  // 知识库事件
  (e: 'delete-file', filename: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const localDrawer = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

// 标签页状态
const activeTab = ref('history');

// 历史对话相关
const renameDialog = ref(false);
const renameTitle = ref('');
const currentRenameId = ref<number | null>(null);

const handleNewConversation = () => {
  emit('new');
};

const handleSelectConversation = (conversationId: number) => {
  emit('select', conversationId);
};

const handleDeleteConversation = (conversationId: number) => {
  emit('delete', conversationId);
};

const handleRenameConversation = (conv: Conversation) => {
  currentRenameId.value = conv.id;
  renameTitle.value = conv.title;
  renameDialog.value = true;
};

const confirmRename = () => {
  if (currentRenameId.value && renameTitle.value.trim()) {
    emit('rename', currentRenameId.value, renameTitle.value.trim());
    renameDialog.value = false;
    renameTitle.value = '';
    currentRenameId.value = null;
  }
};

// 知识库相关
const fileInput = ref<HTMLInputElement | null>(null);
const isDragging = ref(false);

const triggerUpload = () => {
  if (!props.isUploading) fileInput.value?.click();
};

const handleDragover = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = true;
};

const handleDragleave = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;
};

const handleDropInternal = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;
  props.handleDrop(e);
};

// 时间格式化
const formatDate = (dateString: string) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  
  if (isNaN(date.getTime())) {
    return '';
  }
  
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60));
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60));
      return minutes <= 0 ? '刚刚' : `${minutes}分钟前`;
    }
    return `${hours}小时前`;
  } else if (days === 1) {
    return '昨天';
  } else if (days < 7) {
    return `${days}天前`;
  } else {
    return date.toLocaleDateString('zh-CN', { 
      year: 'numeric',
      month: 'short', 
      day: 'numeric' 
    });
  }
};
</script>

<style scoped>
.unified-sidebar {
  z-index: 1000;
  background-color: #ffffff;
  border-right: none;
}

.sidebar-tabs {
  border-bottom: none;
}

.sidebar-content {
  height: calc(100% - 48px);
  overflow-y: auto;
  background-color: #fafafa;
}

/* 自定义滚动条 */
.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.25);
}

.conversation-item {
  transition: all 0.2s ease;
  border-left: none;
}

.conversation-item:hover {
  background-color: rgba(33, 150, 243, 0.06) !important;
}

.conversation-active {
  background-color: rgba(33, 150, 243, 0.1) !important;
}

.conversation-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}


.knowledge-item {
  transition: all 0.2s ease;
  border-left: none;
}

.knowledge-item:hover {
  background-color: rgba(33, 150, 243, 0.06) !important;
  transform: translateX(2px);
}

.delete-btn {
  display: none;
}

.knowledge-item:hover .delete-btn {
  display: inline-flex;
}

.knowledge-item:hover .status-icon {
  display: none;
}
</style>

